"""
Phase 2.0 Orchestration Runtime — the background side of the outbox.

Provides:
  - drain(): poll + publish outbox events (single implementation shared by the
    asyncio worker, the Celery beat task, and tests).
  - SystemJobDriver: advances ObservationJob state on behalf of the edge
    orchestrator (no tenant/user required), emitting outbox events.
  - process_observation_events(): in simulation mode, consumes PUBLISHED
    OBSERVATION_JOB.* events and drives the execution phase of the lifecycle.
  - metrics(): health/backpressure summary for the ops endpoint.
"""
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.contact import ObservationJob
from models.events import JobEvent, OutboxEvent
from services.outbox import emit, publish_pending
from services.state_machine import JOB_SM, JOB_TERMINAL_STATES

logger = logging.getLogger(__name__)

SYSTEM_ACTOR = "system:orchestrator"

# Execution-phase chain the simulated edge orchestrator drives automatically.
# Early planning transitions (REQUESTED..SCHEDULED) stay user/orchestrator-driven.
SIMULATED_CHAIN = [
    "QUEUED", "DISPATCHED", "ACKNOWLEDGED", "PREPARING",
    "EXECUTING", "RECEIVING", "PROCESSING", "COMPLETED",
]

SIMULATE = os.environ.get("AFRIGROUND_ORCHESTRATION_SIMULATE", "1") == "1"


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SystemJobDriver:
    """Advances observation jobs without a user tenant (actor = system)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def advance(
        self,
        job_id: uuid.UUID,
        to_state: str,
        reason: str = "",
        actor: str = SYSTEM_ACTOR,
    ) -> ObservationJob:
        job = await self.db.get(ObservationJob, job_id)
        if not job:
            logger.warning("system advance skipped: job %s not found", job_id)
            return None
        if job.status in JOB_TERMINAL_STATES:
            return job

        from_state = job.status
        JOB_SM.validate(from_state, to_state)
        job.status = to_state
        if to_state in ("COMPLETED", "PARTIAL_SUCCESS", "FAILED"):
            job.completed_at = _now()
        if to_state == "FAILED" and reason:
            job.failure_reason = reason

        self.db.add(
            JobEvent(
                observation_job_id=job.id,
                from_state=from_state,
                to_state=to_state,
                actor=actor,
                reason=reason or f"System transition {from_state} -> {to_state}",
            )
        )
        emit(
            self.db,
            aggregate_type="observation_job",
            aggregate_id=job.id,
            event_type=f"OBSERVATION_JOB.{to_state}",
            payload={
                "job_id": str(job.id),
                "from_state": from_state,
                "to_state": to_state,
                "reason": reason,
                "org_id": str(job.org_id) if job.org_id else None,
            },
        )
        await self.db.flush()

        if to_state in ("COMPLETED", "PARTIAL_SUCCESS", "FAILED"):
            from services.sla import SLAService

            try:
                await SLAService(self.db).enforce_job(job)
            except Exception:  # noqa: BLE001
                logger.exception("sla enforcement failed for job %s", job.id)

        if to_state == "COMPLETED":
            from services.delivery import DeliveryService

            try:
                await DeliveryService(self.db).on_job_completed(job)
            except Exception:  # noqa: BLE001
                logger.exception("delivery pipeline failed for job %s", job.id)

        return job


async def process_observation_events(db: AsyncSession, simulate: bool = SIMULATE) -> int:
    """Consume PUBLISHED OBSERVATION_JOB.* events.

    In simulate mode the runtime stands in for the edge agent, advancing each
    job one step along SIMULATED_CHAIN. Returns the number of transitions applied.
    Idempotent: only events describing the job's current state drive a change.
    """
    stmt = (
        select(OutboxEvent)
        .where(
            OutboxEvent.status == "PUBLISHED",
            OutboxEvent.aggregate_type == "observation_job",
            OutboxEvent.event_type.like("OBSERVATION_JOB.%"),
        )
        .order_by(OutboxEvent.created_at)
        .limit(200)
    )
    result = await db.execute(stmt)
    events = result.scalars().all()

    driver = SystemJobDriver(db)
    applied = 0
    for event in events:
        if not simulate:
            continue
        payload = event.payload or {}
        current = payload.get("to_state")
        if current not in SIMULATED_CHAIN:
            continue
        idx = SIMULATED_CHAIN.index(current)
        if idx + 1 >= len(SIMULATED_CHAIN):
            continue  # COMPLETED: nothing left to drive
        target = SIMULATED_CHAIN[idx + 1]

        job = await db.get(ObservationJob, event.aggregate_id)
        if not job or job.status != current:
            continue  # stale or duplicate event; no-op

        await driver.advance(job.id, target, reason="Simulated edge agent")
        applied += 1

    if applied:
        await db.commit()
    return applied


async def dispatch_due_jobs(db: AsyncSession, lead_s: Optional[float] = None) -> int:
    """System-side dispatcher (real-agent mode): transition QUEUED jobs to
    DISPATCHED when their scheduled contact is within the dispatch lead window
    (default: settings.agent_dispatch_lead_s) or already underway.

    Real edge agents poll for DISPATCHED jobs; the simulated runtime skips this
    (process_observation_events drives DISPATCHED itself).
    """
    from models.contact import ScheduledContact as SC
    from config import settings as _settings

    lead = lead_s if lead_s is not None else _settings.agent_dispatch_lead_s
    cutoff = _now() + timedelta(seconds=lead)
    rows = (
        await db.execute(
            select(ObservationJob.id, SC.scheduled_start)
            .join(SC, SC.id == ObservationJob.scheduled_contact_id)
            .where(
                ObservationJob.status == "QUEUED",
                SC.scheduled_start <= cutoff,
            )
            .order_by(SC.scheduled_start)
            .limit(100)
        )
    ).all()

    driver = SystemJobDriver(db)
    dispatched = 0
    for job_id, _start in rows:
        job = await db.get(ObservationJob, job_id)
        if not job or job.status != "QUEUED":
            continue
        await driver.advance(job.id, "DISPATCHED", reason="Dispatch lead reached")
        dispatched += 1

    if dispatched:
        await db.commit()
        logger.info("orchestrator: dispatched %d job(s) to edge agents", dispatched)
    return dispatched


async def drain(session_factory, limit: int = 50) -> dict:
    """Poll outbox events, publish them, fan out to per-org webhooks, and
    (in real-agent mode) dispatch due jobs to edge agents.
    Shared by worker + Celery task."""
    async with session_factory() as db:
        published = await publish_pending(db, limit=limit)
        from services.webhooks import deliver_org_webhooks

        fan_out = await deliver_org_webhooks(db)

        dispatched = 0
        if not SIMULATE:
            dispatched = await dispatch_due_jobs(db)
        return {"published": published, "webhooks": fan_out, "dispatched": dispatched}


async def metrics(db: AsyncSession) -> dict:
    """Outbox health/backpressure summary for the ops endpoint."""
    now = _now()

    total, pending, published, failed = (
        await db.execute(
            select(
                func.count(OutboxEvent.id),
                func.count(OutboxEvent.id).filter(OutboxEvent.status == "PENDING"),
                func.count(OutboxEvent.id).filter(OutboxEvent.status == "PUBLISHED"),
                func.count(OutboxEvent.id).filter(OutboxEvent.status == "FAILED"),
            )
        )
    ).one()

    oldest_pending = (
        await db.execute(
            select(func.min(OutboxEvent.created_at)).where(OutboxEvent.status == "PENDING")
        )
    ).scalar_one_or_none()

    attempts = (
        await db.execute(select(func.coalesce(func.sum(OutboxEvent.attempt_count), 0)))
    ).scalar_one()

    retry_due = (
        await db.execute(
            select(func.count(OutboxEvent.id)).where(
                OutboxEvent.status == "FAILED",
                OutboxEvent.next_retry_at.isnot(None),
                OutboxEvent.next_retry_at <= now,
            )
        )
    ).scalar_one()

    job_status = (
        await db.execute(
            select(ObservationJob.status, func.count(ObservationJob.id))
            .group_by(ObservationJob.status)
        )
    ).all()

    return {
        "outbox": {
            "total": total,
            "by_status": {"PENDING": pending, "PUBLISHED": published, "FAILED": failed},
            "oldest_pending_at": oldest_pending.isoformat() if oldest_pending else None,
            "oldest_pending_age_s": round((now - oldest_pending).total_seconds(), 1) if oldest_pending else None,
            "total_attempts": attempts,
            "retry_due": retry_due,
            "backpressure": pending + retry_due,
            "simulate": SIMULATE,
        },
        "jobs_by_status": {status: count for status, count in job_status},
        "generated_at": now.isoformat(),
    }