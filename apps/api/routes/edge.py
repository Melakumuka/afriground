"""
API Routes — Edge Agent Ingestion (Phase 2.1/2.2): heartbeat, time-status,
telemetry, quality. Tenant-scoped for now (mTLS bridging is a later phase).

Station-Led Configuration (Step 5) additions — the local Station Gateway
polls/executes against these:
    GET  /api/v1/edge/jobs/assigned                pull jobs + profiles
    POST /api/v1/edge/jobs/{job_id}/readiness      push engineer checklist
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from services.edge_agent import (
    EdgeAgentService,
    HeartbeatRequest,
    QualityResponse,
    TelemetryRequest,
    TelemetryResponse,
    TimeStatusRequest,
)
from services.readiness import StationReadinessService
from services.tenancy import TenantContext, get_tenant_context

router = APIRouter(prefix="/api/v1/edge", tags=["Edge Agents"])


class ReadinessRequest(BaseModel):
    status: str  # READY, NOT_READY
    checklist_results: dict = Field(default_factory=dict)
    engineer_id: Optional[uuid.UUID] = None


@router.post("/stations/{station_id}/agents/{agent_id}/heartbeat")
async def report_heartbeat(
    station_id: uuid.UUID,
    agent_id: str,
    req: HeartbeatRequest,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("station.manage")
    service = EdgeAgentService(db, tenant)
    hb = await service.report_heartbeat(
        station_id, agent_id, agent_version=req.agent_version, metrics=req.metrics
    )
    return {
        "id": str(hb.id),
        "station_id": str(hb.station_id),
        "agent_id": hb.agent_id,
        "received_at": hb.received_at,
    }


@router.post("/stations/{station_id}/agents/{agent_id}/time-status")
async def report_time_status(
    station_id: uuid.UUID,
    agent_id: str,
    req: TimeStatusRequest,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("station.manage")
    service = EdgeAgentService(db, tenant)
    row = await service.report_time_status(
        station_id, agent_id,
        sync_status=req.sync_status,
        offset_ms=req.offset_ms,
        clock_source=req.clock_source,
    )
    return {
        "id": str(row.id),
        "station_id": str(row.station_id),
        "sync_status": row.sync_status,
        "offset_ms": row.offset_ms,
        "clock_source": row.clock_source,
        "reported_at": row.reported_at,
    }


@router.post("/stations/{station_id}/agents/{agent_id}/telemetry", response_model=TelemetryResponse)
async def ingest_telemetry(
    station_id: uuid.UUID,
    agent_id: str,
    req: TelemetryRequest,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("station.manage")
    service = EdgeAgentService(db, tenant)
    row = await service.ingest_telemetry(
        station_id, agent_id, telemetry_type=req.telemetry_type, payload=req.payload
    )
    return TelemetryResponse(
        id=row.id,
        station_id=row.station_id,
        agent_id=row.agent_id,
        telemetry_type=row.telemetry_type,
        payload=row.payload or {},
        recorded_at=row.recorded_at,
    )


@router.get("/stations/{station_id}/telemetry", response_model=List[TelemetryResponse])
async def list_telemetry(
    station_id: uuid.UUID,
    telemetry_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    service = EdgeAgentService(db, tenant)
    rows = await service.list_telemetry(station_id, telemetry_type=telemetry_type, limit=limit)
    return [
        TelemetryResponse(
            id=r.id, station_id=r.station_id, agent_id=r.agent_id,
            telemetry_type=r.telemetry_type, payload=r.payload or {}, recorded_at=r.recorded_at,
        )
        for r in rows
    ]


@router.get("/stations/{station_id}/quality", response_model=QualityResponse)
async def station_quality(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    service = EdgeAgentService(db, tenant)
    row = await service.latest_quality(station_id)
    if not row:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="No quality score computed yet")
    return QualityResponse(
        station_id=row.station_id,
        score=row.score,
        availability=row.availability,
        reliability=row.reliability,
        timeliness=row.timeliness,
        calculated_at=row.calculated_at,
    )


@router.post("/stations/{station_id}/quality/recompute", response_model=QualityResponse)
async def recompute_quality(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("station.manage")
    service = EdgeAgentService(db, tenant)
    row = await service.recompute_quality(station_id)
    return QualityResponse(
        station_id=row.station_id,
        score=row.score,
        availability=row.availability,
        reliability=row.reliability,
        timeliness=row.timeliness,
        calculated_at=row.calculated_at,
    )


# ═════════════════════════════════════════════════════════════════════════════
# Station Gateway endpoints (Steps 3-6 of Station-Led Configuration)
# ═════════════════════════════════════════════════════════════════════════════


class JobAcknowledgeRequest(BaseModel):
    agent_id: str


class ReceiptRequest(BaseModel):
    observation_job_id: uuid.UUID
    status: str  # COMPLETED, PARTIAL_SUCCESS, FAILED
    actual_start: Optional[str] = None
    actual_end: Optional[str] = None
    carrier_locked: Optional[bool] = None
    symbol_locked: Optional[bool] = None
    data_volume_bytes: Optional[float] = None
    frame_count: Optional[int] = None
    average_ebno: Optional[float] = None
    tracking_error_summary: Optional[dict] = None
    time_source: Optional[str] = None
    clock_offset_ms: Optional[float] = None
    weather_summary: Optional[dict] = None
    pass_report_hash: Optional[str] = None
    artifact_manifest_hash: Optional[str] = None
    agent_signature: Optional[str] = None
    signature_algorithm: Optional[str] = None
    notes: Optional[str] = None


class ArtifactUploadRequest(BaseModel):
    job_id: uuid.UUID
    filenames: List[str]


# ── Assigned jobs (Edge pulls) ───────────────────────────────────────────────

@router.get("/stations/{station_id}/jobs/assigned")
async def get_assigned_jobs(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Edge Agent polls this to discover jobs dispatched to its station."""
    from models.contact import ObservationJob, ScheduledContact

    result = await db.execute(
        select(ObservationJob)
        .join(ScheduledContact, ObservationJob.scheduled_contact_id == ScheduledContact.id)
        .where(
            ScheduledContact.station_id == station_id,
            ObservationJob.org_id == tenant.org_id,
            ObservationJob.status.in_(["DISPATCHED", "ACKNOWLEDGED", "PREPARING", "QUEUED"]),
        )
        .order_by(ScheduledContact.scheduled_start)
    )
    jobs = result.scalars().all()
    return [
        {
            "id": str(j.id),
            "status": j.status,
            "readiness_status": j.readiness_status,
            "mission_profile_id": str(j.mission_profile_id),
            "station_operation_profile_id": str(j.station_operation_profile_id) if j.station_operation_profile_id else None,
            "scheduled_contact_id": str(j.scheduled_contact_id),
            "priority": j.priority,
            "tx_requested": j.tx_requested,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        }
        for j in jobs
    ]


# ── Job acknowledge (Edge confirms receipt) ──────────────────────────────────

@router.post("/jobs/{job_id}/acknowledge")
async def acknowledge_job(
    job_id: uuid.UUID,
    req: JobAcknowledgeRequest,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Edge Agent acknowledges it has received the job assignment."""
    from services.orchestrator import ObservationOrchestrator

    orch = ObservationOrchestrator(db, tenant)
    job = await orch.transition(job_id, "ACKNOWLEDGED", reason=f"Acknowledged by agent {req.agent_id}")
    return {"id": str(job.id), "status": job.status}


# ── Readiness (engineer checklist confirmation) ──────────────────────────────

@router.post("/jobs/{job_id}/readiness")
async def submit_readiness(
    job_id: uuid.UUID,
    req: ReadinessRequest,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Edge Agent pushes engineer's READY / NOT_READY checklist result."""
    service = StationReadinessService(db, tenant)
    event, job = await service.record_readiness(
        job_id=job_id,
        status=req.status,
        checklist_results=req.checklist_results,
        engineer_id=req.engineer_id,
    )
    return {
        "id": str(event.id),
        "job_id": str(event.job_id),
        "status": event.status,
        "readiness_status": job.readiness_status,
        "confirmed_at": event.confirmed_at.isoformat() if event.confirmed_at else None,
    }


# ── Execution receipts ──────────────────────────────────────────────────────

@router.post("/receipts")
async def submit_receipt(
    req: ReceiptRequest,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Edge Agent submits execution receipt after pass completion."""
    from models.contact import ExecutionReceipt
    from datetime import datetime

    receipt = ExecutionReceipt(
        observation_job_id=req.observation_job_id,
        status=req.status,
        actual_start=datetime.fromisoformat(req.actual_start) if req.actual_start else None,
        actual_end=datetime.fromisoformat(req.actual_end) if req.actual_end else None,
        carrier_locked=req.carrier_locked,
        symbol_locked=req.symbol_locked,
        data_volume_bytes=req.data_volume_bytes,
        frame_count=req.frame_count,
        average_ebno=req.average_ebno,
        tracking_error_summary=req.tracking_error_summary,
        time_source=req.time_source,
        clock_offset_ms=req.clock_offset_ms,
        weather_summary=req.weather_summary,
        pass_report_hash=req.pass_report_hash,
        artifact_manifest_hash=req.artifact_manifest_hash,
        agent_signature=req.agent_signature,
        signature_algorithm=req.signature_algorithm,
        notes=req.notes,
    )
    db.add(receipt)
    await db.flush()

    # Finalize the job status so data delivery pipelines trigger
    from services.orchestrator import ObservationOrchestrator
    orch = ObservationOrchestrator(db, tenant)
    
    # We must ensure the status is a valid terminal state (COMPLETED, FAILED, PARTIAL_SUCCESS)
    if req.status in ["COMPLETED", "FAILED", "PARTIAL_SUCCESS"]:
        await orch.transition(req.observation_job_id, req.status, reason="Execution receipt received from Edge Agent")
    else:
        await db.commit()

    await db.refresh(receipt)
    return {
        "id": str(receipt.id),
        "observation_job_id": str(receipt.observation_job_id),
        "status": receipt.status,
        "received_at": receipt.received_at.isoformat() if receipt.received_at else None,
    }


# ── Profiles (Edge pulls certified profiles) ────────────────────────────────

@router.get("/stations/{station_id}/profiles")
async def get_station_profiles(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Edge Agent pulls certified StationOperationProfiles for its station."""
    from models.station_twin import StationOperationProfile

    result = await db.execute(
        select(StationOperationProfile).where(
            StationOperationProfile.station_id == station_id,
        )
    )
    profiles = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "station_id": str(p.station_id),
            "mission_profile_id": str(p.mission_profile_id),
            "satellite_id": str(p.satellite_id) if p.satellite_id else None,
            "certification_state": p.certification_state,
            "operation_mode": p.operation_mode,
            "status": p.status,
            "success_rate": p.success_rate,
            "total_passes": p.total_passes,
            "last_used_at": p.last_used_at.isoformat() if p.last_used_at else None,
        }
        for p in profiles
    ]


@router.get("/profiles/{profile_id}")
async def get_profile_detail(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Edge Agent pulls full profile detail including config payloads."""
    from models.station_twin import StationOperationProfile

    p = await db.get(StationOperationProfile, profile_id)
    if not p:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "id": str(p.id),
        "name": p.name,
        "station_id": str(p.station_id),
        "mission_profile_id": str(p.mission_profile_id),
        "satellite_id": str(p.satellite_id) if p.satellite_id else None,
        "certification_state": p.certification_state,
        "operation_mode": p.operation_mode,
        "mcs_profile_payload": p.mcs_profile_payload,
        "hdr_config_payload": p.hdr_config_payload,
        "acu_config_payload": p.acu_config_payload,
        "rf_path_payload": p.rf_path_payload,
        "decoder_config_payload": p.decoder_config_payload,
        "safety_payload": p.safety_payload,
        "success_rate": p.success_rate,
        "total_passes": p.total_passes,
    }


# ── Artifact upload pre-signed URLs ─────────────────────────────────────────

@router.post("/artifacts/upload-request")
async def request_artifact_upload(
    req: ArtifactUploadRequest,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Edge Agent requests pre-signed S3/MinIO URLs for artifact upload (Phase 8.1 Smart Routing)."""
    from models.contact import ObservationJob
    from models.data import DataDeliveryDestination
    from services.storage import StorageService
    from core.crypto import decrypt_dict
    from config import settings

    # 1. Look up the job to find the customer org_id
    job = await db.get(ObservationJob, req.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="ObservationJob not found")

    # 2. Check for active egress destinations for this org
    stmt = select(DataDeliveryDestination).where(
        DataDeliveryDestination.org_id == job.org_id,
        DataDeliveryDestination.is_active == True
    )
    result = await db.execute(stmt)
    destinations = result.scalars().all()

    urls = {}
    target_type = "afriground_minio"
    used_dest_id = None

    if destinations:
        # Use the first active destination (Smart Routing)
        dest = destinations[0]
        # Decrypt config symmetrically
        if "encrypted_payload" in dest.config:
            config = decrypt_dict(dest.config["encrypted_payload"])
        else:
            config = dest.config
            
        target_type = "customer_cloud"
        used_dest_id = str(dest.id)
        
        for filename in req.filenames:
            key = f"artifacts/{req.job_id}/{filename}"
            urls[filename] = StorageService.generate_presigned_url(
                dest_type=dest.type,
                config=config,
                key=key,
                expires_in=3600
            )
    else:
        # Fallback to AfriGround MinIO
        fallback_config = {
            "access_key": settings.s3_access_key,
            "secret_key": settings.s3_secret_key,
            "endpoint": settings.s3_endpoint_url,
            "bucket": "afriground-raw"
        }
        for filename in req.filenames:
            key = f"artifacts/{req.job_id}/{filename}"
            urls[filename] = StorageService.generate_presigned_url(
                dest_type="s3",
                config=fallback_config,
                key=key,
                expires_in=3600
            )

    return {
        "job_id": str(req.job_id), 
        "upload_urls": urls,
        "target_type": target_type,
        "destination_id": used_dest_id
    }