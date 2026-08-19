"""
SLA Enforcement (Phase 3.0) — evaluates mission SLAs when an observation job
reaches a terminal state and records breaches.

Per-mission SLA targets are declared on MissionSLA. Job-level metrics that can
be evaluated at completion:

  - timeliness / latency  (unit=seconds): wall-clock processing time from job
    creation to completion. Target is a maximum.
  - success_rate          (unit=percent): 100 on success, 0 on failure. Target
    is a minimum.

Availability/uptime targets are window-level and evaluated over a reporting
window (future phase); job-level enforcement covers the per-execution SLAs.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.contact import ObservationJob
from models.mission import MissionProfile, MissionSLA, SLASLAViolation
from services.outbox import emit

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SLAService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def enforce_job(self, job: ObservationJob) -> List[SLASLAViolation]:
        """Evaluate all SLAs for the job's mission against its outcome.

        Creates an SLASLAViolation row + emits SLA.VIOLATION for each breach.
        Idempotent: a (job, sla_type) breach is recorded at most once.
        The caller owns the transaction.
        """
        if job.status not in ("COMPLETED", "PARTIAL_SUCCESS", "FAILED"):
            return []

        slas = await self._mission_slas(job.mission_profile_id)
        if not slas:
            return []

        violations: List[SLASLAViolation] = []
        for sla in slas:
            actual, unit = await self._measure(job, sla.sla_type)
            if actual is None:
                continue
            if not self._breached(sla.sla_type, actual, sla.target_value):
                continue

            existing = (
                await self.db.execute(
                    select(SLASLAViolation.id).where(
                        SLASLAViolation.observation_job_id == job.id,
                        SLASLAViolation.sla_type == sla.sla_type,
                    )
                )
            ).scalar_one_or_none()
            if existing:
                continue

            violation = SLASLAViolation(
                mission_id=sla.mission_id,
                observation_job_id=job.id,
                sla_type=sla.sla_type,
                target_value=sla.target_value,
                actual_value=round(actual, 2),
                unit=unit,
                status="open",
                violated_at=_now(),
            )
            self.db.add(violation)
            await self.db.flush()
            emit(
                self.db,
                aggregate_type="sla_violation",
                aggregate_id=violation.id,
                event_type="SLA.VIOLATION",
                payload={
                    "violation_id": str(violation.id),
                    "mission_id": str(sla.mission_id),
                    "job_id": str(job.id),
                    "sla_type": sla.sla_type,
                    "target": sla.target_value,
                    "actual": violation.actual_value,
                    "unit": unit,
                },
            )
            violations.append(violation)

        if violations:
            logger.warning(
                "sla: %d breach(es) recorded for job %s", len(violations), job.id
            )
        return violations

    async def list_violations(
        self,
        org_id: Optional[uuid.UUID] = None,
        mission_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[SLASLAViolation]:
        stmt = select(SLASLAViolation)
        if org_id:
            stmt = stmt.join(ObservationJob, ObservationJob.id == SLASLAViolation.observation_job_id).where(
                ObservationJob.org_id == org_id
            )
        if mission_id:
            stmt = stmt.where(SLASLAViolation.mission_id == mission_id)
        if status:
            stmt = stmt.where(SLASLAViolation.status == status)
        stmt = stmt.order_by(SLASLAViolation.violated_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _mission_slas(self, mission_profile_id: uuid.UUID) -> List[MissionSLA]:
        profile = await self.db.get(MissionProfile, mission_profile_id)
        if not profile:
            return []
        result = await self.db.execute(
            select(MissionSLA).where(MissionSLA.mission_id == profile.mission_id)
        )
        return list(result.scalars().all())

    async def _measure(self, job: ObservationJob, sla_type: str) -> tuple[Optional[float], Optional[str]]:
        if sla_type in ("timeliness", "latency"):
            if not job.completed_at or not job.created_at:
                return None, None
            seconds = (job.completed_at - job.created_at).total_seconds()
            return max(seconds, 0.0), "seconds"
        if sla_type == "success_rate":
            success = job.status in ("COMPLETED", "PARTIAL_SUCCESS")
            return (100.0 if success else 0.0), "percent"
        return None, None

    @staticmethod
    def _breached(sla_type: str, actual: float, target: float) -> bool:
        if sla_type in ("timeliness", "latency"):
            return actual > target  # must be faster than target
        return actual < target  # percent-type SLAs are minimums