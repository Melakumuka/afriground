"""
Edge Agent data foundation (Phase 2.1/2.2) — heartbeat & time-sync ingestion,
structured telemetry, missed-heartbeat watchdog, and station quality recompute.

Heartbeats/time/telemetry are tenant-scoped when reported via the API; the
watchdog runs system-side from the orchestration runtime.
"""
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.station import GroundStation, Incident
from models.station_twin import (
    StationAgentIdentity,
    StationHeartbeat,
    StationQualityScore,
    StationTelemetryReading,
    StationTimeStatus,
)
from services.outbox import emit
from services.tenancy import TenantContext, write_audit_log

logger = logging.getLogger(__name__)

HEARTBEAT_THRESHOLD_S = 120.0
TIME_OFFSET_DEGRADE_MS = 100.0

SYSTEM_ACTOR = "system:watchdog"


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Schemas ──────────────────────────────────────────────────────────────────

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


class TelemetryResponse(BaseModel):
    id: uuid.UUID
    station_id: uuid.UUID
    agent_id: str
    telemetry_type: str
    payload: dict
    recorded_at: Optional[datetime] = None


class QualityResponse(BaseModel):
    station_id: uuid.UUID
    score: float
    availability: Optional[float] = None
    reliability: Optional[float] = None
    timeliness: Optional[float] = None
    calculated_at: Optional[datetime] = None


# ── Service ──────────────────────────────────────────────────────────────────

class EdgeAgentService:
    """Heartbeat/time/telemetry ingestion. Tenant-scoped for the management
    API; tenant=None when called from the mTLS agent bridge (identity is the
    authorization — the station is resolved from the agent identity)."""

    def __init__(self, db: AsyncSession, tenant: Optional[TenantContext] = None):
        self.db = db
        self.tenant = tenant

    async def _get_station(self, station_id: uuid.UUID) -> GroundStation:
        station = await self.db.get(GroundStation, station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        if self.tenant and station.org_id != self.tenant.org_id:
            raise HTTPException(status_code=404, detail="Station not found")
        return station

    async def _get_agent(self, station_id: uuid.UUID, agent_id: str) -> StationAgentIdentity:
        agent = (
            await self.db.execute(
                select(StationAgentIdentity).where(
                    StationAgentIdentity.station_id == station_id,
                    StationAgentIdentity.agent_id == agent_id,
                )
            )
        ).scalars().first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent identity not found")
        return agent

    async def _audit(self, action: str, resource_type: str, resource_id: uuid.UUID, details: dict) -> None:
        if self.tenant:
            await write_audit_log(
                self.db, self.tenant, action=action,
                resource_type=resource_type, resource_id=resource_id, details=details,
            )

    async def register_agent(
        self,
        station_id: uuid.UUID,
        agent_id: str,
        agent_version: str = "",
        public_key_pem: str = "",
    ) -> StationAgentIdentity:
        station = await self._get_station(station_id)
        agent = StationAgentIdentity(
            station_id=station.id,
            agent_id=agent_id,
            agent_version=agent_version,
            public_key_pem=public_key_pem,
            last_heartbeat_at=_now(),
            status="active",
        )
        self.db.add(agent)
        await self._audit(
            action="agent.register",
            resource_type="ground_station", resource_id=station.id,
            details={"agent_id": agent_id},
        )
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def report_heartbeat(
        self,
        station_id: uuid.UUID,
        agent_id: str,
        agent_version: str = "",
        metrics: Optional[dict] = None,
    ) -> StationHeartbeat:
        station = await self._get_station(station_id)
        agent = await self._get_agent(station_id, agent_id)

        now = _now()
        agent.last_heartbeat_at = now
        agent.status = "active"
        if agent_version:
            agent.agent_version = agent_version

        heartbeat = StationHeartbeat(
            station_id=station.id,
            agent_id=agent_id,
            agent_version=agent_version or agent.agent_version,
            metrics=metrics or {},
            received_at=now,
        )
        self.db.add(heartbeat)
        emit(
            self.db,
            aggregate_type="station",
            aggregate_id=station.id,
            event_type="AGENT.HEARTBEAT",
            payload={"station_id": str(station.id), "agent_id": agent_id},
        )
        await self.db.commit()
        await self.db.refresh(heartbeat)
        return heartbeat

    async def report_time_status(
        self,
        station_id: uuid.UUID,
        agent_id: str,
        sync_status: str = "SYNCED",
        offset_ms: float = 0.0,
        clock_source: str = "ntp",
    ) -> StationTimeStatus:
        station = await self._get_station(station_id)
        await self._get_agent(station_id, agent_id)

        row = StationTimeStatus(
            station_id=station.id,
            sync_status=sync_status,
            offset_ms=offset_ms,
            last_sync_at=_now() if sync_status in ("SYNCED", "SYNCING") else None,
            clock_source=clock_source,
            reported_at=_now(),
        )
        self.db.add(row)

        if sync_status in ("UNSYNCED", "DEGRADED") or offset_ms > TIME_OFFSET_DEGRADE_MS:
            if station.status != "offline":
                station.status = "degraded"

        emit(
            self.db,
            aggregate_type="station",
            aggregate_id=station.id,
            event_type="AGENT.TIME_STATUS",
            payload={
                "station_id": str(station.id),
                "sync_status": sync_status,
                "offset_ms": offset_ms,
            },
        )
        await self._audit(
            action="agent.time_status",
            resource_type="ground_station", resource_id=station.id,
            details={"sync_status": sync_status, "offset_ms": offset_ms},
        )
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def ingest_telemetry(
        self,
        station_id: uuid.UUID,
        agent_id: str,
        telemetry_type: str,
        payload: Optional[dict] = None,
    ) -> StationTelemetryReading:
        station = await self._get_station(station_id)
        await self._get_agent(station_id, agent_id)

        reading = StationTelemetryReading(
            station_id=station.id,
            agent_id=agent_id,
            telemetry_type=telemetry_type,
            payload=payload or {},
            recorded_at=_now(),
        )
        self.db.add(reading)

        await self._maybe_open_incident(station, telemetry_type, payload or {})

        await self.db.commit()
        await self.db.refresh(reading)
        return reading

    async def _maybe_open_incident(self, station: GroundStation, telemetry_type: str, payload: dict) -> None:
        """Surface operational incidents from critical telemetry."""
        critical = False
        severity, description = "medium", ""
        if telemetry_type == "power" and payload.get("main") is False:
            critical, severity, description = True, "high", "Main power failure reported by edge agent"
        elif telemetry_type == "signal" and payload.get("snr_db", 99.0) < 3.0:
            critical, severity, description = True, "medium", "Signal quality below threshold (SNR < 3 dB)"

        if not critical:
            return

        open_count = (
            await self.db.execute(
                select(func.count(Incident.id)).where(
                    Incident.station_id == station.id,
                    Incident.status.in_(["open", "investigating", "identified"]),
                )
            )
        ).scalar_one()
        if open_count:
            return  # already surfaced

        self.db.add(
            Incident(
                station_id=station.id,
                severity=severity,
                status="open",
                description=description,
            )
        )
        emit(
            self.db,
            aggregate_type="station",
            aggregate_id=station.id,
            event_type="STATION.INCIDENT_OPENED",
            payload={"station_id": str(station.id), "severity": severity, "description": description},
        )
        await self._audit(
            action="station.incident_auto",
            resource_type="ground_station", resource_id=station.id,
            details={"severity": severity, "description": description},
        )

    async def list_telemetry(
        self,
        station_id: uuid.UUID,
        telemetry_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[StationTelemetryReading]:
        await self._get_station(station_id)
        stmt = (
            select(StationTelemetryReading)
            .where(StationTelemetryReading.station_id == station_id)
            .order_by(StationTelemetryReading.recorded_at.desc())
            .limit(limit)
        )
        if telemetry_type:
            stmt = stmt.where(StationTelemetryReading.telemetry_type == telemetry_type)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def recompute_quality(self, station_id: uuid.UUID) -> StationQualityScore:
        """Compute and persist a StationQualityScore from live signals."""
        station = await self._get_station(station_id)
        now = _now()

        # Availability: station status + recency of heartbeats.
        availability = {"operational": 100.0, "degraded": 60.0, "maintenance": 20.0, "offline": 0.0}.get(
            station.status, 50.0
        )
        last_hb = (
            await self.db.execute(
                select(func.max(StationHeartbeat.received_at)).where(
                    StationHeartbeat.station_id == station.id
                )
            )
        ).scalar_one_or_none()
        if last_hb and (now - last_hb).total_seconds() > HEARTBEAT_THRESHOLD_S:
            availability = min(availability, 30.0)

        # Reliability: signal stats from recent telemetry (SNR 0..25 dB -> 0..100).
        avg_snr = (
            await self.db.execute(
                select(func.avg((StationTelemetryReading.payload["snr_db"]).as_float())).where(
                    StationTelemetryReading.station_id == station.id,
                    StationTelemetryReading.telemetry_type == "signal",
                )
            )
        ).scalar_one_or_none()
        reliability = 95.0
        if avg_snr is not None:
            reliability = max(10.0, min(100.0, (float(avg_snr) / 25.0) * 100.0))

        # Timeliness: time-sync offsets reported (0..200ms -> 100..0).
        max_offset = (
            await self.db.execute(
                select(func.max(StationTimeStatus.offset_ms)).where(
                    StationTimeStatus.station_id == station.id
                )
            )
        ).scalar_one_or_none()
        timeliness = 100.0
        if max_offset is not None:
            timeliness = max(0.0, min(100.0, 100.0 - float(max_offset) / 2.0))

        score = round(0.4 * availability + 0.3 * reliability + 0.3 * timeliness, 1)
        row = StationQualityScore(
            station_id=station.id,
            score=score,
            availability=round(availability, 1),
            reliability=round(reliability, 1),
            timeliness=round(timeliness, 1),
            period_start=now - timedelta(minutes=5),
            period_end=now,
            calculated_at=now,
        )
        self.db.add(row)
        await self._audit(
            action="station.quality",
            resource_type="ground_station", resource_id=station.id,
            details={"score": score},
        )
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def latest_quality(self, station_id: uuid.UUID) -> Optional[StationQualityScore]:
        await self._get_station(station_id)
        row = (
            await self.db.execute(
                select(StationQualityScore)
                .where(StationQualityScore.station_id == station_id)
                .order_by(StationQualityScore.calculated_at.desc())
            )
        ).scalars().first()
        return row


# ── System watchdog (runs from the orchestration runtime, no tenant) ────────

async def check_missed_heartbeats(db: AsyncSession, threshold_s: float = HEARTBEAT_THRESHOLD_S) -> int:
    """Flag stations whose active agents stopped heartbeating and surface incidents."""
    cutoff = _now() - timedelta(seconds=threshold_s)
    stale_agents = (
        await db.execute(
            select(StationAgentIdentity).where(
                StationAgentIdentity.status == "active",
                StationAgentIdentity.last_heartbeat_at.isnot(None),
                StationAgentIdentity.last_heartbeat_at < cutoff,
            )
        )
    ).scalars().all()

    flagged = 0
    for agent in stale_agents:
        station = await db.get(GroundStation, agent.station_id)
        if not station:
            continue
        if station.status == "degraded":
            continue  # already flagged
        station.status = "degraded"
        emit(
            db,
            aggregate_type="station",
            aggregate_id=station.id,
            event_type="STATION.DEGRADED",
            payload={
                "station_id": str(station.id),
                "agent_id": agent.agent_id,
                "reason": f"Missed heartbeat for {threshold_s:g}s",
            },
        )
        open_count = (
            await db.execute(
                select(func.count(Incident.id)).where(
                    Incident.station_id == station.id,
                    Incident.status.in_(["open", "investigating", "identified"]),
                )
            )
        ).scalar_one()
        if not open_count:
            db.add(
                Incident(
                    station_id=station.id,
                    severity="medium",
                    status="open",
                    description=f"Edge agent {agent.agent_id} missed heartbeat",
                )
            )
        flagged += 1

    if flagged:
        await db.commit()
        logger.info("watchdog flagged %d station(s) as degraded", flagged)
    return flagged