"""
Edge Agent Dispatch Service (Phase 4.0) — the machine-facing contract between
the afriground-station-agent and the orchestration runtime.

The agent authenticates via mTLS (services/agent_auth.py) and may only touch
jobs whose scheduled contact is assigned to its station. It fetches DISPATCHED
work, acknowledges it, drives the execution chain (ACKNOWLEDGED -> PREPARING ->
EXECUTING -> RECEIVING -> PROCESSING -> terminal), and submits execution
receipts. All state changes go through SystemJobDriver so outbox events, job
events, SLA enforcement, and data delivery stay consistent with the
user-driven and simulated paths.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.contact import ExecutionReceipt, ObservationJob, ScheduledContact
from models.mission import Mission, MissionProfile, MissionRFProfile
from models.station import GroundStation
from models.station_twin import StationAgentIdentity
from services.orchestration_runtime import SystemJobDriver

logger = logging.getLogger(__name__)

# Execution-phase states an edge agent may drive itself into (Phase 4.0).
AGENT_CHAIN = [
    "ACKNOWLEDGED", "PREPARING", "EXECUTING", "RECEIVING",
    "PROCESSING", "COMPLETED", "PARTIAL_SUCCESS", "FAILED",
]


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ReceiptRequest(BaseModel):
    status: str  # COMPLETED, PARTIAL_SUCCESS, FAILED
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    received_bytes: Optional[float] = None
    recorded_file_url: Optional[str] = None
    signal_quality: Optional[dict] = Field(default_factory=dict)
    notes: Optional[str] = None


class AgentDispatchService:
    def __init__(self, db: AsyncSession, agent: StationAgentIdentity, station: GroundStation):
        self.db = db
        self.agent = agent
        self.station = station
        self.driver = SystemJobDriver(db)

    # ── Job lookup (station-scoped) ──────────────────────────────────────────

    async def assigned_jobs(self, statuses: Optional[List[str]] = None) -> List[ObservationJob]:
        """Jobs scheduled on this agent's station in the given states
        (default: DISPATCHED — work the agent is expected to fetch)."""
        statuses = statuses or ["DISPATCHED"]
        stmt = (
            select(ObservationJob)
            .join(ScheduledContact, ScheduledContact.id == ObservationJob.scheduled_contact_id)
            .where(
                ScheduledContact.station_id == self.station.id,
                ObservationJob.status.in_(statuses),
            )
            .order_by(ObservationJob.created_at)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_job(self, job_id: uuid.UUID) -> ObservationJob:
        job = await self.db.get(ObservationJob, job_id)
        if not job or not await self._job_on_station(job):
            raise HTTPException(status_code=404, detail="Job not found on this station")
        return job

    # ── State transitions ────────────────────────────────────────────────────

    async def acknowledge(self, job_id: uuid.UUID) -> ObservationJob:
        job = await self.get_job(job_id)
        if job.status != "DISPATCHED":
            raise HTTPException(status_code=409, detail=f"Job is {job.status}, expected DISPATCHED")
        return await self.driver.advance(job.id, "ACKNOWLEDGED", reason="Acknowledged by edge agent",
                                         actor=f"agent:{self.agent.agent_id}")

    async def transition(self, job_id: uuid.UUID, to_state: str, reason: str = "") -> ObservationJob:
        """Agent-driven execution-chain transition (validated against AGENT_CHAIN)."""
        if to_state not in AGENT_CHAIN:
            raise HTTPException(status_code=400, detail=f"State {to_state} is not agent-driven")
        job = await self.get_job(job_id)
        if job.status not in AGENT_CHAIN:
            raise HTTPException(
                status_code=409,
                detail=f"Job is {job.status}; agent chain starts at ACKNOWLEDGED",
            )
        return await self.driver.advance(job.id, to_state, reason=reason or f"Reported by edge agent",
                                         actor=f"agent:{self.agent.agent_id}")

    # ── Execution receipts ───────────────────────────────────────────────────

    async def submit_receipt(self, job_id: uuid.UUID, receipt: ReceiptRequest) -> ExecutionReceipt:
        """Persist an execution receipt; terminal state is applied if the job
        has not reached it yet. Idempotent per job (one receipt kept)."""
        job = await self.get_job(job_id)
        if receipt.status not in ("COMPLETED", "PARTIAL_SUCCESS", "FAILED"):
            raise HTTPException(status_code=400, detail="Receipt status must be a terminal state")

        existing = (
            await self.db.execute(
                select(ExecutionReceipt).where(ExecutionReceipt.observation_job_id == job.id)
            )
        ).scalars().first()
        if existing:
            raise HTTPException(status_code=409, detail="Receipt already submitted for this job")

        row = ExecutionReceipt(
            observation_job_id=job.id,
            status=receipt.status,
            actual_start=receipt.actual_start,
            actual_end=receipt.actual_end,
            received_bytes=receipt.received_bytes,
            recorded_file_url=receipt.recorded_file_url,
            signal_quality=receipt.signal_quality or {},
            notes=receipt.notes,
        )
        self.db.add(row)
        await self.db.flush()

        if job.status != receipt.status:
            job = await self.transition(job.id, receipt.status, reason="Execution receipt submitted")

        await self.db.commit()
        await self.db.refresh(row)
        logger.info("agent %s: receipt for job %s -> %s", self.agent.agent_id, job.id, receipt.status)
        return row

    # ── Job detail bundle for the agent ──────────────────────────────────────

    async def job_bundle(self, job: ObservationJob) -> dict:
        """Everything the agent needs to execute: contact window, RF config,
        mission metadata, and TX request."""
        contact = await self.db.get(ScheduledContact, job.scheduled_contact_id)
        rf = None
        mission_name = None
        profile = await self.db.get(MissionProfile, job.mission_profile_id)
        if profile:
            mission = await self.db.get(Mission, profile.mission_id)
            if mission:
                mission_name = mission.name
            rf = (
                await self.db.execute(
                    select(MissionRFProfile).where(
                        MissionRFProfile.mission_profile_id == profile.id,
                        MissionRFProfile.is_active == True,  # noqa: E712
                    )
                )
            ).scalars().first()

        return {
            "job_id": str(job.id),
            "status": job.status,
            "priority": job.priority,
            "tx_requested": job.tx_requested,
            "mission": mission_name,
            "scheduled_contact": {
                "id": str(contact.id),
                "start": contact.scheduled_start.isoformat(),
                "end": contact.scheduled_end.isoformat(),
            },
            "rf": {
                "band": rf.band if rf else None,
                "uplink_frequency_hz": rf.uplink_frequency_hz if rf else None,
                "downlink_frequency_hz": rf.downlink_frequency_hz if rf else None,
                "max_tx_power_dbm": rf.max_tx_power_dbm if rf else None,
            },
        }

    # ── Helpers ──────────────────────────────────────────────────────────────

    async def _job_on_station(self, job: ObservationJob) -> bool:
        contact = await self.db.get(ScheduledContact, job.scheduled_contact_id)
        return bool(contact and contact.station_id == self.station.id)