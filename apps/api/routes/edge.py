"""
API Routes — Edge Agent Ingestion (Phase 2.1/2.2): heartbeat, time-status,
telemetry, quality. Tenant-scoped for now (mTLS bridging is a later phase).
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
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
from services.tenancy import TenantContext, get_tenant_context

router = APIRouter(prefix="/api/v1/edge", tags=["Edge Agents"])


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