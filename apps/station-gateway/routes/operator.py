from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging

from local_db import get_db, CachedJob, CachedProfile
from cloud_client import CloudClient
from adapters import get_adapter
from config import settings
import os

logger = logging.getLogger(__name__)

router = APIRouter()

# Get the absolute path to the templates directory
current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(os.path.dirname(current_dir), "templates")
templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    """Station Dashboard — health overview and upcoming pass queue."""
    adapter = get_adapter(settings.adapter_type)
    health = await adapter.get_station_health()

    # Fetch upcoming jobs from local DB
    result = await db.execute(select(CachedJob).order_by(CachedJob.scheduled_start))
    jobs = result.scalars().all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "health": health,
        "jobs": jobs,
        "station_id": settings.station_id,
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

    # If job is completed, try to get cached receipt artifacts
    receipt = None
    if job.status == "COMPLETED":
        adapter = get_adapter(settings.adapter_type)
        try:
            receipt = await adapter.collect_pass_artifacts()
        except Exception as e:
            logger.warning(f"Could not collect receipt for completed job {job_id}: {e}")

    return templates.TemplateResponse("pass_console.html", {
        "request": request,
        "job": job,
        "profile": profile,
        "receipt": receipt,
        "station_id": settings.station_id,
    })


@router.post("/jobs/{job_id}/ready")
async def confirm_ready(
    job_id: str,
    mcs_loaded: Optional[str] = Form(None),
    hdr_configured: Optional[str] = Form(None),
    acu_tle_updated: Optional[str] = Form(None),
    rf_verified: Optional[str] = Form(None),
    weather_safe: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Engineer confirms readiness — pushes StationReadinessEvent to Cloud."""
    checklist_results = {
        "mcs_profile_loaded": mcs_loaded is not None,
        "hdr_configured": hdr_configured is not None,
        "acu_tle_updated": acu_tle_updated is not None,
        "rf_path_verified": rf_verified is not None,
        "weather_safe": weather_safe is not None,
    }

    logger.info(f"Engineer confirmed readiness for job {job_id}: {checklist_results}")

    # Push to cloud
    client = CloudClient()
    try:
        await client.submit_readiness(job_id, status="READY", checklist_results=checklist_results)
    except Exception as e:
        logger.error(f"Failed to submit readiness to cloud for job {job_id}: {e}")
        # Even if cloud is down, update local state so the UI reflects it

    # Update local state
    job = await db.get(CachedJob, job_id)
    if job:
        job.readiness_status = "READY"
        await db.commit()

    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)


@router.post("/jobs/{job_id}/abort")
async def emergency_abort(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Emergency abort — LOCAL-FIRST. Stops recording, kills TX, stows antenna."""
    logger.critical(f"🚨 EMERGENCY ABORT triggered for job {job_id}")

    # Step 1: Local hardware commands (do NOT depend on cloud connectivity)
    adapter = get_adapter(settings.adapter_type)
    try:
        await adapter.stop_pass_recording()
        logger.info(f"[ABORT] Recording stopped for job {job_id}")
    except Exception as e:
        logger.error(f"[ABORT] Failed to stop recording: {e}")
        
    try:
        await adapter.kill_tx()
        logger.info(f"[ABORT] TX killed for job {job_id}")
    except Exception as e:
        logger.error(f"[ABORT] Failed to kill TX: {e}")
        
    try:
        await adapter.emergency_stow()
        logger.info(f"[ABORT] Emergency stow commanded for job {job_id}")
    except Exception as e:
        logger.error(f"[ABORT] Failed to stow antenna: {e}")

    # Step 2: Update local DB
    job = await db.get(CachedJob, job_id)
    if job:
        job.status = "FAILED"
        job.readiness_status = "ABORTED"
        await db.commit()

    # Step 3: Best-effort notify the cloud (non-blocking)
    client = CloudClient()
    try:
        await client.submit_readiness(job_id, status="ABORTED", checklist_results={"emergency_abort": True})
    except Exception as e:
        logger.warning(f"[ABORT] Could not notify cloud (offline?): {e}")

    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)
