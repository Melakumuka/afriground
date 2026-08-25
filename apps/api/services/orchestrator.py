"""
Observation Orchestrator — drives ObservationJob lifecycle with a strict state
machine, recording every transition and emitting transactional outbox events.
Layer 2 orchestration from docs/implementation_plan.md (Phase 1.4).
"""
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.contact import (
    ObservationJob,
    ExecutionReceipt,
    ScheduledContact,
)
from models.events import JobEvent
from services.outbox import emit
from services.state_machine import JOB_SM, JOB_TERMINAL_STATES
from services.tenancy import TenantContext, write_audit_log


class JobNotFound(HTTPException):
    def __init__(self, job_id: uuid.UUID):
        super().__init__(status_code=404, detail=f"Observation job {job_id} not found")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ObservationOrchestrator:
    def __init__(self, db: AsyncSession, tenant: TenantContext):
        self.db = db
        self.tenant = tenant

    async def _get_job(self, job_id: uuid.UUID) -> ObservationJob:
        job = await self.db.get(ObservationJob, job_id)
        if not job or job.org_id != self.tenant.org_id:
            raise JobNotFound(job_id)
        return job

    async def _record_transition(
        self,
        job: ObservationJob,
        to_state: str,
        reason: str = "",
        actor: Optional[str] = None,
    ) -> None:
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
                actor=actor or f"{self.tenant.user.id}",
                reason=reason,
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
                "org_id": str(self.tenant.org_id) if self.tenant.org_id else None,
            },
        )
        await write_audit_log(
            self.db,
            self.tenant,
            action="job.transition",
            resource_type="observation_job",
            resource_id=job.id,
            details={"from_state": from_state, "to_state": to_state, "reason": reason},
        )

    # ── Creation ────────────────────────────────────────────────────────────

    async def create_job(
        self,
        scheduled_contact_id: uuid.UUID,
        mission_profile_id: uuid.UUID,
        priority: int = 5,
        tx_requested: bool = False,
        station_operation_profile_id: Optional[uuid.UUID] = None,
    ) -> ObservationJob:
        contact = await self.db.get(ScheduledContact, scheduled_contact_id)
        if not contact or contact.org_id != self.tenant.org_id:
            raise HTTPException(status_code=404, detail="Scheduled contact not found")

        existing = (
            await self.db.execute(
                select(ObservationJob).where(
                    ObservationJob.scheduled_contact_id == scheduled_contact_id,
                    ObservationJob.org_id == self.tenant.org_id,
                )
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"An observation job already exists for scheduled contact {scheduled_contact_id}",
            )

        job = ObservationJob(
            org_id=self.tenant.org_id,
            scheduled_contact_id=scheduled_contact_id,
            mission_profile_id=mission_profile_id,
            station_operation_profile_id=station_operation_profile_id,
            status="DRAFT",
            priority=priority,
            tx_requested=tx_requested,
        )
        self.db.add(job)
        await self.db.flush()

        self.db.add(
            JobEvent(
                observation_job_id=job.id,
                from_state=None,
                to_state="DRAFT",
                actor=str(self.tenant.user.id),
                reason="Job created",
            )
        )
        emit(
            self.db,
            aggregate_type="observation_job",
            aggregate_id=job.id,
            event_type="OBSERVATION_JOB.CREATED",
            payload={"job_id": str(job.id), "org_id": str(self.tenant.org_id) if self.tenant.org_id else None},
        )
        await self.db.commit()
        await self.db.refresh(job)
        return job

    # ── Transitions ─────────────────────────────────────────────────────────

    async def transition(
        self,
        job_id: uuid.UUID,
        to_state: str,
        reason: str = "",
        actor: Optional[str] = None,
    ) -> ObservationJob:
        job = await self._get_job(job_id)
        if job.status in JOB_TERMINAL_STATES:
            raise HTTPException(
                status_code=400,
                detail=f"Job is in terminal state '{job.status}' and cannot transition",
            )
        if to_state == "QUEUED" and job.status == "FAILED":
            if job.retry_count >= job.max_retries:
                raise HTTPException(status_code=400, detail="Maximum retry count exceeded")
            job.retry_count += 1
        await self._record_transition(job, to_state, reason, actor)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def request(self, job_id: uuid.UUID, actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "REQUESTED", actor=actor)

    async def validate(self, job_id: uuid.UUID, actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "VALIDATING", actor=actor)

    async def schedule(self, job_id: uuid.UUID, actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "SCHEDULED", actor=actor)

    async def fail(self, job_id: uuid.UUID, reason: str = "", actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "FAILED", reason or "Job failed", actor)

    async def enqueue(self, job_id: uuid.UUID, actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "QUEUED", actor=actor)

    async def dispatch(self, job_id: uuid.UUID, actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "DISPATCHED", actor=actor)

    async def acknowledge(self, job_id: uuid.UUID, actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "ACKNOWLEDGED", actor=actor)

    async def prepare(self, job_id: uuid.UUID, actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "PREPARING", actor=actor)

    async def execute(self, job_id: uuid.UUID, actor: Optional[str] = None) -> ObservationJob:
        job = await self._get_job(job_id)
        # Station-Led Configuration (Step 5): expensive hardware is never
        # auto-executed — a READY StationReadinessEvent from the local engineer
        # is mandatory before EXECUTING.
        from services.readiness import StationReadinessService

        event = await StationReadinessService(self.db, self.tenant).require_ready(job)
        
        # Check for TX redundancy SPOF
        if job.tx_requested and event and event.checklist_results.get("crt_redundancy") == "spof":
            raise HTTPException(
                status_code=409, 
                detail="S-Band TX SPOF active. Cannot execute TX job."
            )
            
        if not job.started_at:
            job.started_at = _now()
        return await self.transition(job_id, "EXECUTING", actor=actor)

    async def receive(self, job_id: uuid.UUID, actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "RECEIVING", actor=actor)

    async def process(self, job_id: uuid.UUID, actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "PROCESSING", actor=actor)

    async def complete(self, job_id: uuid.UUID, actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "COMPLETED", actor=actor)

    async def partial_success(self, job_id: uuid.UUID, reason: str = "", actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "PARTIAL_SUCCESS", reason or "Partial success", actor)

    async def cancel(self, job_id: uuid.UUID, reason: str = "", actor: Optional[str] = None) -> ObservationJob:
        return await self.transition(job_id, "CANCELLED", reason or "Cancelled", actor)

    # ── Receipts ────────────────────────────────────────────────────────────

    async def record_receipt(
        self,
        job_id: uuid.UUID,
        status: str,
        actual_start: Optional[datetime] = None,
        actual_end: Optional[datetime] = None,
        received_bytes: Optional[float] = None,
        recorded_file_url: Optional[str] = None,
        signal_quality: Optional[dict] = None,
        notes: str = "",
    ) -> ExecutionReceipt:
        job = await self._get_job(job_id)
        if status not in ("COMPLETED", "PARTIAL_SUCCESS", "FAILED"):
            raise HTTPException(status_code=400, detail="Receipt status must be a terminal job state")

        receipt = ExecutionReceipt(
            observation_job_id=job.id,
            status=status,
            actual_start=actual_start,
            actual_end=actual_end,
            received_bytes=received_bytes,
            recorded_file_url=recorded_file_url,
            signal_quality=signal_quality or {},
            notes=notes,
        )
        self.db.add(receipt)
        await self.db.flush()

        # Finalize the job to match the receipt status.
        await self._record_transition(job, status, reason=notes or "Execution receipt finalized", actor=str(self.tenant.user.id))

        emit(
            self.db,
            aggregate_type="execution_receipt",
            aggregate_id=receipt.id,
            event_type="EXECUTION_RECEIPT.RECEIVED",
            payload={
                "job_id": str(job.id),
                "status": status,
                "received_bytes": received_bytes,
                "org_id": str(self.tenant.org_id) if self.tenant.org_id else None,
            },
        )
        await self.db.commit()
        await self.db.refresh(receipt)
        return receipt

    # ── Queries ─────────────────────────────────────────────────────────────

    async def list_jobs(self, status: Optional[str] = None, limit: int = 100) -> List[ObservationJob]:
        stmt = select(ObservationJob).where(ObservationJob.org_id == self.tenant.org_id)
        if status:
            stmt = stmt.where(ObservationJob.status == status.upper())
        stmt = stmt.order_by(ObservationJob.created_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_events(self, job_id: uuid.UUID) -> List[JobEvent]:
        job = await self._get_job(job_id)
        stmt = (
            select(JobEvent)
            .where(JobEvent.observation_job_id == job.id)
            .order_by(JobEvent.created_at)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_receipts(self, job_id: uuid.UUID) -> List[ExecutionReceipt]:
        job = await self._get_job(job_id)
        stmt = (
            select(ExecutionReceipt)
            .where(ExecutionReceipt.observation_job_id == job.id)
            .order_by(ExecutionReceipt.received_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())