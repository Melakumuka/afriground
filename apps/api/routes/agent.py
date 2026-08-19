"""
API Routes — Edge Agent Bridge (Phase 4.0): machine-facing endpoints for the
afriground-station-agent. Authenticated by mTLS client certificate
(services/agent_auth.py); the agent identity IS the authorization — every
operation is scoped to the agent's own station. No tenant JWT required.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from services.agent_auth import AgentIdentity, get_agent_identity
from services.agent_dispatch import AgentDispatchService, ReceiptRequest
from services.edge_agent import EdgeAgentService

router = APIRouter(prefix="/api/v1/agent", tags=["Edge Agent Bridge"])


class StateRequest(BaseModel):
    to_state: str
    reason: str = ""


class HeartbeatRequest(BaseModel):
    agent_version: str = ""
    metrics: dict = Field(default_factory=dict)


class TimeStatusRequest(BaseModel):
    sync_status: str = "SYNCED"  # SYNCED, SYNCING, UNSYNCED, DEGRADED
    offset_ms: float = 0.0
    clock_source: str = "ntp"


class TelemetryRequest(BaseModel):
    telemetry_type: str  # antenna, rf, signal, weather, power, recording
    payload: dict = Field(default_factory=dict)


@router.get("/jobs")
async def assigned_jobs(
    statuses: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    identity: AgentIdentity = Depends(get_agent_identity),
):
    """Fetch the jobs assigned to this agent's station (DISPATCHED by default)."""
    svc = AgentDispatchService(db, identity.agent, identity.station)
    jobs = await svc.assigned_jobs(statuses=statuses)
    return {"station_id": str(identity.station.id), "jobs": [await svc.job_bundle(j) for j in jobs]}


@router.get("/jobs/{job_id}")
async def job_detail(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    identity: AgentIdentity = Depends(get_agent_identity),
):
    svc = AgentDispatchService(db, identity.agent, identity.station)
    job = await svc.get_job(job_id)
    return await svc.job_bundle(job)


@router.post("/jobs/{job_id}/ack")
async def acknowledge_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    identity: AgentIdentity = Depends(get_agent_identity),
):
    svc = AgentDispatchService(db, identity.agent, identity.station)
    job = await svc.acknowledge(job_id)
    await db.commit()
    return {"job_id": str(job.id), "status": job.status}


@router.post("/jobs/{job_id}/state")
async def report_state(
    job_id: uuid.UUID,
    req: StateRequest,
    db: AsyncSession = Depends(get_db_session),
    identity: AgentIdentity = Depends(get_agent_identity),
):
    svc = AgentDispatchService(db, identity.agent, identity.station)
    job = await svc.transition(job_id, req.to_state, reason=req.reason)
    await db.commit()
    return {"job_id": str(job.id), "status": job.status}


@router.post("/jobs/{job_id}/receipt")
async def submit_receipt(
    job_id: uuid.UUID,
    req: ReceiptRequest,
    db: AsyncSession = Depends(get_db_session),
    identity: AgentIdentity = Depends(get_agent_identity),
):
    svc = AgentDispatchService(db, identity.agent, identity.station)
    receipt = await svc.submit_receipt(job_id, req)
    return {
        "receipt_id": str(receipt.id),
        "job_id": str(receipt.observation_job_id),
        "status": receipt.status,
    }


@router.post("/heartbeat")
async def agent_heartbeat(
    req: HeartbeatRequest,
    db: AsyncSession = Depends(get_db_session),
    identity: AgentIdentity = Depends(get_agent_identity),
):
    service = EdgeAgentService(db)
    hb = await service.report_heartbeat(
        identity.station.id, identity.agent.agent_id,
        agent_version=req.agent_version, metrics=req.metrics,
    )
    return {
        "id": str(hb.id),
        "station_id": str(hb.station_id),
        "agent_id": hb.agent_id,
        "received_at": hb.received_at,
    }


@router.post("/time-status")
async def agent_time_status(
    req: TimeStatusRequest,
    db: AsyncSession = Depends(get_db_session),
    identity: AgentIdentity = Depends(get_agent_identity),
):
    service = EdgeAgentService(db)
    row = await service.report_time_status(
        identity.station.id, identity.agent.agent_id,
        sync_status=req.sync_status, offset_ms=req.offset_ms, clock_source=req.clock_source,
    )
    return {
        "id": str(row.id),
        "sync_status": row.sync_status,
        "offset_ms": row.offset_ms,
        "reported_at": row.reported_at,
    }


@router.post("/telemetry")
async def agent_telemetry(
    req: TelemetryRequest,
    db: AsyncSession = Depends(get_db_session),
    identity: AgentIdentity = Depends(get_agent_identity),
):
    service = EdgeAgentService(db)
    row = await service.ingest_telemetry(
        identity.station.id, identity.agent.agent_id,
        telemetry_type=req.telemetry_type, payload=req.payload,
    )
    return {
        "id": str(row.id),
        "station_id": str(row.station_id),
        "telemetry_type": row.telemetry_type,
        "recorded_at": row.recorded_at,
    }