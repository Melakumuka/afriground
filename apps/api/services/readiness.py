"""
Station Readiness (Station-Led Configuration & Local Gateway, Step 5).

The cloud can never auto-execute against expensive hardware: a job may only
transition to EXECUTING when a StationReadinessEvent with status READY exists
for it (recorded by the local engineer through the Station Gateway).
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.contact import ObservationJob, StationReadinessEvent
from services.outbox import emit
from services.tenancy import TenantContext, write_audit_log


class ReadinessRequired(HTTPException):
    def __init__(self, job_id: uuid.UUID):
        super().__init__(
            status_code=409,
            detail=f"Engineer readiness confirmation (READY) required before execution for job {job_id}",
        )


def _now() -> datetime:
    return datetime.now(timezone.utc)


class StationReadinessService:
    def __init__(self, db: AsyncSession, tenant: TenantContext):
        self.db = db
        self.tenant = tenant

    async def _get_job(self, job_id: uuid.UUID) -> ObservationJob:
        job = await self.db.get(ObservationJob, job_id)
        if not job or job.org_id != self.tenant.org_id:
            raise HTTPException(status_code=404, detail=f"Observation job {job_id} not found")
        return job

    async def latest_readiness(self, job_id: uuid.UUID) -> Optional[StationReadinessEvent]:
        """Most recent readiness confirmation for a job (multiple confirmations
        are allowed over time; the latest one governs the gate)."""
        result = await self.db.execute(
            select(StationReadinessEvent)
            .where(StationReadinessEvent.job_id == job_id)
            .order_by(StationReadinessEvent.confirmed_at.desc(), StationReadinessEvent.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def record_readiness(
        self,
        job_id: uuid.UUID,
        status: str,
        checklist_results: Optional[dict] = None,
        engineer_id: Optional[uuid.UUID] = None,
    ) -> tuple[StationReadinessEvent, ObservationJob]:
        """Persist the engineer's manual confirmation and update the job's
        readiness_status snapshot (used by the orchestrator gate)."""
        if status not in ("READY", "NOT_READY"):
            raise HTTPException(status_code=400, detail="Readiness status must be READY or NOT_READY")

        job = await self._get_job(job_id)

        event = StationReadinessEvent(
            job_id=job.id,
            engineer_id=engineer_id,
            confirmed_at=_now(),
            checklist_results=checklist_results or {},
            status=status,
        )
        self.db.add(event)
        job.readiness_status = status
        await self.db.flush()

        emit(
            self.db,
            aggregate_type="observation_job",
            aggregate_id=job.id,
            event_type="OBSERVATION_JOB.READINESS",
            payload={
                "job_id": str(job.id),
                "readiness": status,
                "checklist_results": checklist_results or {},
                "org_id": str(self.tenant.org_id) if self.tenant.org_id else None,
            },
        )
        await write_audit_log(
            self.db,
            self.tenant,
            action="job.readiness",
            resource_type="observation_job",
            resource_id=job.id,
            details={"readiness": status, "checklist_results": checklist_results or {}},
        )
        await self.db.commit()
        await self.db.refresh(event)
        await self.db.refresh(job)
        return event, job

    async def require_ready(self, job: ObservationJob) -> Optional[StationReadinessEvent]:
        """Gate check: raise ReadinessRequired unless a READY confirmation exists,
        OR the profile is configured for AUTOMATIC operation."""
        from models.station_twin import StationOperationProfile

        if job.station_operation_profile_id:
            profile = await self.db.get(StationOperationProfile, job.station_operation_profile_id)
            if profile and profile.operation_mode == "AUTOMATIC":
                return None  # No manual readiness required

        event = await self.latest_readiness(job.id)
        if not event or event.status != "READY":
            raise ReadinessRequired(job.id)
        return event