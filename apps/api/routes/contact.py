"""
API Routes — Contact Planning & Observation Jobs (Phase 1.4)
"""
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from models.contact import ObservationJob
from services.contact_planning import ContactPlanningService
from services.orchestrator import ObservationOrchestrator
from services.tenancy import TenantContext, get_tenant_context

router = APIRouter(prefix="/api/v1/contact", tags=["Contact Planning & Jobs"])


# ── Visibility opportunities ────────────────────────────────────────────────

@router.post("/visibility")
async def generate_visibility_opportunities(
    spacecraft_id: uuid.UUID,
    station_ids: List[uuid.UUID],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    min_elevation_deg: float = Query(5.0),
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("contact.plan")
    service = ContactPlanningService(db, tenant)
    vis = await service.generate_visibility_opportunities(
        spacecraft_id, station_ids, start, end, min_elevation_deg
    )
    return [
        {
            "id": str(v.id),
            "spacecraft_id": str(v.spacecraft_id),
            "station_id": str(v.station_id),
            "aos": v.aos,
            "los": v.los,
            "max_elevation_deg": v.max_elevation_deg,
            "duration_seconds": v.duration_seconds,
            "status": v.status,
        }
        for v in vis
    ]


@router.post("/opportunities")
async def create_contact_opportunities(
    visibility_ids: List[uuid.UUID],
    mission_profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("contact.plan")
    service = ContactPlanningService(db, tenant)
    opps = await service.create_contact_opportunities(visibility_ids, mission_profile_id)
    return [
        {
            "id": str(o.id),
            "visibility_opportunity_id": str(o.visibility_opportunity_id),
            "mission_profile_id": str(o.mission_profile_id),
            "required_band": o.required_band,
            "estimated_duration_seconds": o.estimated_duration_seconds,
            "opportunity_score": o.opportunity_score,
            "status": o.status,
        }
        for o in opps
    ]


@router.post("/plan")
async def plan_contact(
    spacecraft_id: uuid.UUID,
    mission_profile_id: uuid.UUID,
    customer_org_id: uuid.UUID,
    station_ids: List[uuid.UUID],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("contact.plan")
    service = ContactPlanningService(db, tenant)
    return await service.plan_contact(spacecraft_id, mission_profile_id, customer_org_id, station_ids, start, end)


# ── Reservations ────────────────────────────────────────────────────────────

@router.post("/reservations")
async def create_reservation(
    contact_opportunity_id: uuid.UUID,
    customer_org_id: uuid.UUID,
    spacecraft_id: uuid.UUID,
    mission_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("contact.plan")
    service = ContactPlanningService(db, tenant)
    res = await service.create_reservation(contact_opportunity_id, customer_org_id, spacecraft_id, mission_id)
    return {
        "id": str(res.id),
        "contact_opportunity_id": str(res.contact_opportunity_id),
        "customer_org_id": str(res.customer_org_id),
        "spacecraft_id": str(res.spacecraft_id),
        "status": res.status,
        "expires_at": res.expires_at,
    }


@router.post("/reservations/{reservation_id}/confirm")
async def confirm_reservation(
    reservation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("contact.plan")
    service = ContactPlanningService(db, tenant)
    res = await service.confirm_reservation(reservation_id)
    return {"id": str(res.id), "status": res.status, "confirmed_at": res.confirmed_at}


@router.post("/scheduled-contacts")
async def schedule_contact(
    reservation_id: uuid.UUID,
    scheduled_start: Optional[datetime] = None,
    scheduled_end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("contact.plan")
    service = ContactPlanningService(db, tenant)
    contact = await service.schedule_contact(reservation_id, scheduled_start, scheduled_end)
    return {
        "id": str(contact.id),
        "reservation_id": str(contact.reservation_id),
        "station_id": str(contact.station_id),
        "spacecraft_id": str(contact.spacecraft_id),
        "scheduled_start": contact.scheduled_start,
        "scheduled_end": contact.scheduled_end,
        "status": contact.status,
    }


# ── Observation jobs ────────────────────────────────────────────────────────

@router.post("/jobs")
async def create_job(
    scheduled_contact_id: uuid.UUID,
    mission_profile_id: uuid.UUID,
    priority: int = Query(5),
    tx_requested: bool = Query(False),
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("job.operate")
    orchestrator = ObservationOrchestrator(db, tenant)
    job = await orchestrator.create_job(scheduled_contact_id, mission_profile_id, priority, tx_requested)
    return _job_dict(job)


@router.get("/jobs")
async def list_jobs(
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    orchestrator = ObservationOrchestrator(db, tenant)
    jobs = await orchestrator.list_jobs(status, limit)
    return [_job_dict(j) for j in jobs]


@router.get("/jobs/{job_id}")
async def get_job_details(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    from sqlalchemy import select
    from models.contact import ExecutionReceipt
    from models.station_twin import StationReadinessEvent
    from fastapi import HTTPException

    stmt = (
        select(ObservationJob)
        .where(ObservationJob.id == job_id)
        .where(ObservationJob.org_id == tenant.org_id)
    )
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job_dict = _job_dict(job)

    # Fetch Readiness Event
    readiness_stmt = select(StationReadinessEvent).where(StationReadinessEvent.job_id == job_id).order_by(StationReadinessEvent.created_at.desc()).limit(1)
    readiness_result = await db.execute(readiness_stmt)
    readiness = readiness_result.scalar_one_or_none()

    if readiness:
        job_dict["readiness"] = {
            "status": readiness.status,
            "confirmed_at": readiness.confirmed_at,
            "checklist_results": readiness.checklist_results,
            "notes": readiness.notes,
        }

    # Fetch Execution Receipt
    # Note: Using the original execution_receipts from contact if any, or the new edge one
    # If the edge receipt model is different, we query it. 
    receipt_stmt = select(ExecutionReceipt).where(ExecutionReceipt.job_id == job_id).order_by(ExecutionReceipt.created_at.desc()).limit(1)
    receipt_result = await db.execute(receipt_stmt)
    receipt = receipt_result.scalar_one_or_none()

    if receipt:
        job_dict["receipt"] = {
            "status": receipt.status if hasattr(receipt, 'status') else 'COMPLETED',
            "carrier_locked": getattr(receipt, 'carrier_locked', None),
            "symbol_locked": getattr(receipt, 'symbol_locked', None),
            "data_volume_bytes": getattr(receipt, 'data_volume_bytes', getattr(receipt, 'received_bytes', None)),
            "average_ebno": getattr(receipt, 'average_ebno', None),
            "pass_report_hash": getattr(receipt, 'pass_report_hash', None),
        }
        
    return job_dict



@router.post("/jobs/{job_id}/transition")
async def transition_job(
    job_id: uuid.UUID,
    to_state: str,
    reason: str = "",
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("job.operate")
    orchestrator = ObservationOrchestrator(db, tenant)
    job = await orchestrator.transition(job_id, to_state.upper(), reason)
    return _job_dict(job)


@router.get("/jobs/{job_id}/events")
async def list_job_events(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    orchestrator = ObservationOrchestrator(db, tenant)
    events = await orchestrator.list_events(job_id)
    return [
        {
            "id": str(e.id),
            "from_state": e.from_state,
            "to_state": e.to_state,
            "actor": e.actor,
            "reason": e.reason,
            "created_at": e.created_at,
        }
        for e in events
    ]


@router.post("/jobs/{job_id}/receipts")
async def record_receipt(
    job_id: uuid.UUID,
    status: str,
    actual_start: Optional[datetime] = None,
    actual_end: Optional[datetime] = None,
    received_bytes: Optional[float] = None,
    recorded_file_url: Optional[str] = None,
    signal_quality: Optional[dict] = None,
    notes: str = "",
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("job.operate")
    orchestrator = ObservationOrchestrator(db, tenant)
    receipt = await orchestrator.record_receipt(
        job_id, status.upper(), actual_start, actual_end,
        received_bytes, recorded_file_url, signal_quality, notes,
    )
    return {
        "id": str(receipt.id),
        "job_id": str(receipt.observation_job_id),
        "status": receipt.status,
        "received_bytes": receipt.received_bytes,
        "received_at": receipt.received_at,
    }


def _job_dict(job: ObservationJob) -> dict:
    return {
        "id": str(job.id),
        "scheduled_contact_id": str(job.scheduled_contact_id),
        "mission_profile_id": str(job.mission_profile_id),
        "status": job.status,
        "priority": job.priority,
        "tx_requested": job.tx_requested,
        "retry_count": job.retry_count,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "failure_reason": job.failure_reason,
    }