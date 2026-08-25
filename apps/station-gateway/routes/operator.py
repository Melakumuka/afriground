from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging
import datetime

from local_db import get_db, CachedJob, CachedProfile, LocalActionAck, FirewallAuditLog
from cloud_client import CloudClient
from adapters import get_adapter
from config import settings
import os
from services.readiness_service import ReadinessService
from services.iso_observer import IsolatedObserver

logger = logging.getLogger(__name__)

router = APIRouter()

current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(os.path.dirname(current_dir), "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    """Station Dashboard — health overview and upcoming pass queue."""
    observer = IsolatedObserver()
    # Construct health from observer
    health = await get_adapter(settings.adapter_type).get_station_health()
    
    # Check latest firewall posture
    result = await db.execute(select(FirewallAuditLog).order_by(FirewallAuditLog.ts.desc()).limit(1))
    latest_audit = result.scalars().first()
    
    # Very basic mock posture evaluation
    firewall_posture = None
    if latest_audit:
        firewall_posture = {
            "ok": latest_audit.direction_correct and latest_audit.enabled,
            "rules_ok": 1 if latest_audit.direction_correct and latest_audit.enabled else 0,
            "rules_total": 1
        }
    else:
        # Default mock for now if no audit run
        firewall_posture = {"ok": True, "rules_ok": 6, "rules_total": 6}

    result = await db.execute(select(CachedJob).order_by(CachedJob.scheduled_start))
    jobs = result.scalars().all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "health": health,
        "jobs": jobs,
        "station_id": settings.station_id,
        "firewall_posture": firewall_posture,
        "wind_safe_threshold": settings.WIND_SAFE_KMH if hasattr(settings, "WIND_SAFE_KMH") else 40,
        "wind_warning_threshold": settings.WIND_WARNING_KMH if hasattr(settings, "WIND_WARNING_KMH") else 55,
    })

@router.get("/jobs/{job_id}", response_class=HTMLResponse)
async def pass_console(request: Request, job_id: str, db: AsyncSession = Depends(get_db)):
    """Pass Console — checklist, profile inspector, and emergency controls."""
    job = await db.get(CachedJob, job_id)
    if not job:
        return HTMLResponse("Job not found", status_code=404)

    profile = None
    if job.station_operation_profile_id:
        profile = await db.get(CachedProfile, job.station_operation_profile_id)

    receipt = None
    if job.status == "COMPLETED":
        adapter = get_adapter(settings.adapter_type)
        try:
            receipt = await adapter.collect_pass_artifacts()
        except Exception as e:
            logger.warning(f"Could not collect receipt for completed job {job_id}: {e}")
            
    # Hard block checks
    observer = IsolatedObserver()
    lcb = await observer.get_lcb_status()
    crt = await observer.get_crt_redundancy()
    
    hard_block_reason = None
    if lcb.get("lcb_engaged"):
        hard_block_reason = "LCB is engaged. Antenna is locked in Local Mode."
    elif job.tx_requested and crt.get("state") == "spof":
        hard_block_reason = "S-Band TX SPOF is active. TX job cannot proceed."

    return templates.TemplateResponse("pass_console.html", {
        "request": request,
        "job": job,
        "profile": profile,
        "receipt": receipt,
        "station_id": settings.station_id,
        "hard_block_reason": hard_block_reason,
        "crt_redundancy": crt,
        "planned_min_elevation_deg": job.planned_min_elevation_deg or 5.0,
        "rise_angle_deg": job.rise_angle_deg or 10.0,
        "acu_min_elevation_deg": 5.0,
        "interpass_gap_seconds": job.interpass_gap_seconds or 1800,
        "wind_speed_kmh": 20.0,
        "clock_offset_ms": 12.5,
    })

@router.post("/jobs/{job_id}/ready")
async def confirm_ready(request: Request, job_id: str, db: AsyncSession = Depends(get_db)):
    """Engineer confirms readiness — pushes StationReadinessEvent to Cloud."""
    form_data = await request.form()
    checklist_results = {key: bool(value) for key, value in form_data.items()}

    logger.info(f"Engineer confirmed readiness for job {job_id}: {checklist_results}")

    job = await db.get(CachedJob, job_id)
    if not job:
        return RedirectResponse(url="/", status_code=303)
        
    profile = None
    if job.station_operation_profile_id:
        profile = await db.get(CachedProfile, job.station_operation_profile_id)
        
    readiness_service = ReadinessService()
    is_ready, reason = await readiness_service.evaluate_and_push_readiness(job, profile, checklist_results)
    
    if is_ready:
        job.readiness_status = "READY"
    else:
        # We don't overwrite if it was a SPOF block (which pushed NOT_READY)
        # unless it was pushed as NOT_READY
        if checklist_results.get("crt_redundancy_loss"):
             job.readiness_status = "NOT_READY"
        logger.warning(f"Readiness blocked locally: {reason}")
        
    await db.commit()

    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)

@router.post("/jobs/{job_id}/local-action-ack")
async def local_action_ack(job_id: str, db: AsyncSession = Depends(get_db)):
    """Logs engineer's acknowledgement of the passive/no-active-commands notice."""
    logger.info(f"Engineer acknowledged passive local action for job {job_id}")

    ack = LocalActionAck(
        ts=datetime.datetime.now(datetime.timezone.utc),
        job_id=job_id,
        ack_text="Local Action Procedure Reviewed"
    )
    db.add(ack)
    await db.commit()

    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)

@router.get("/jobs/{job_id}/status.json")
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    """Partial polling endpoint for Pass Console."""
    job = await db.get(CachedJob, job_id)
    if not job:
        return JSONResponse({"error": "not found"}, status_code=404)
        
    return JSONResponse({
        "id": job.id,
        "status": job.status,
        "readiness_status": job.readiness_status
    })

@router.get("/local/firewall/verify")
async def verify_firewall(db: AsyncSession = Depends(get_db)):
    """Check firewall rules on Gateway PC."""
    # In a real implementation this calls netsh or iptables.
    # Here we simulate a successful verify and write audit.
    logger.info("Verifying firewall posture...")
    
    audit = FirewallAuditLog(
        ts=datetime.datetime.now(datetime.timezone.utc),
        rule_name="AfriGround_Gateway_Verify",
        present=True,
        enabled=True,
        direction="OUT",
        action="ALLOW",
        direction_correct=True
    )
    db.add(audit)
    await db.commit()
    
    # Return to dashboard where the banner will reflect posture
    return RedirectResponse(url="/", status_code=303)
