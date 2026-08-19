"""
RegulatoryAuthorizationService — hard safety gates for TX and station certification.
Defaults: all new stations are tx_disabled and REGISTERED.
See docs/REGULATORY_RULES.md and docs/CERTIFICATION_WORKFLOW.md.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.mission import MissionRFProfile
from models.station import GroundStation
from models.station_twin import (
    StationCapability,
    StationLicense,
    StationCertification,
    StationCertificationEvent,
    StationTimeStatus,
    StationAgentIdentity,
)
from models.core import User
from services.outbox import emit
from services.state_machine import CERTIFICATION_SM
from services.tenancy import TenantContext, write_audit_log


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RegulatoryCheck(BaseModel):
    rule: str
    passed: bool
    detail: str = ""


class RegulatoryCheckResult(BaseModel):
    station_id: uuid.UUID
    authorized: bool
    checks: List[RegulatoryCheck]

    def as_dict(self) -> dict:
        return {
            "station_id": str(self.station_id),
            "authorized": self.authorized,
            "checks": [c.model_dump() for c in self.checks],
        }


class RegulatoryAuthorizationService:
    def __init__(self, db: AsyncSession, tenant: TenantContext):
        self.db = db
        self.tenant = tenant

    # ── Registration ────────────────────────────────────────────────────────

    async def register_station(
        self,
        code: str,
        name: str,
        country: str,
        latitude: float,
        longitude: float,
        altitude_m: float,
        operator_contact_email: Optional[str] = None,
    ) -> GroundStation:
        """Create a station in REGISTERED state with TX safety defaults."""
        from geoalchemy2.elements import WKTElement

        existing = (
            await self.db.execute(select(GroundStation).where(GroundStation.code == code))
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail=f"Station code '{code}' already exists")

        station = GroundStation(
            org_id=self.tenant.org_id,
            name=name,
            code=code,
            country=country,
            latitude=latitude,
            longitude=longitude,
            altitude_m=altitude_m,
            location=WKTElement(f"POINT({longitude} {latitude})", srid=4326),
            certification_state="REGISTERED",
            tx_enabled=False,
            registration_date=_now(),
            operator_contact_email=operator_contact_email,
            status="operational",
        )
        self.db.add(station)
        await self.db.flush()

        cert = StationCertification(
            station_id=station.id,
            current_state="REGISTERED",
        )
        self.db.add(cert)
        await self.db.flush()

        self.db.add(
            StationCertificationEvent(
                station_id=station.id,
                from_state=None,
                to_state="REGISTERED",
                transition_reason="Station registered",
                initiated_by=self.tenant.user.id,
            )
        )
        emit(
            self.db,
            aggregate_type="station",
            aggregate_id=station.id,
            event_type="STATION.REGISTERED",
            payload={"station_id": str(station.id), "code": code, "tx_enabled": False},
        )
        await write_audit_log(
            self.db,
            self.tenant,
            action="station.register",
            resource_type="ground_station",
            resource_id=station.id,
            details={"code": code},
        )
        await self.db.commit()
        await self.db.refresh(station)
        return station

    # ── Certification workflow ─────────────────────────────────────────────

    async def transition_certification(
        self,
        station_id: uuid.UUID,
        to_state: str,
        reason: str = "",
    ) -> StationCertification:
        station = await self._get_station(station_id)
        cert = await self._get_certification(station_id)
        CERTIFICATION_SM.validate(cert.current_state, to_state)

        from_state = cert.current_state
        cert.current_state = to_state
        station.certification_state = to_state
        if to_state == "CERTIFIED":
            cert.certified_at = _now()

        self.db.add(
            StationCertificationEvent(
                station_id=station_id,
                from_state=from_state,
                to_state=to_state,
                transition_reason=reason or f"Transitioned {from_state} -> {to_state}",
                initiated_by=self.tenant.user.id,
            )
        )
        emit(
            self.db,
            aggregate_type="station_certification",
            aggregate_id=cert.id,
            event_type=f"STATION_CERTIFICATION.{to_state}",
            payload={"station_id": str(station_id), "from_state": from_state, "to_state": to_state, "reason": reason},
        )
        await write_audit_log(
            self.db,
            self.tenant,
            action="station.certify",
            resource_type="ground_station",
            resource_id=station_id,
            details={"from_state": from_state, "to_state": to_state, "reason": reason},
        )
        await self.db.commit()
        await self.db.refresh(cert)
        return cert

    async def certify(self, station_id: uuid.UUID, reason: str = "Certified by operator") -> StationCertification:
        return await self.transition_certification(station_id, "CERTIFIED", reason)

    # ── TX authorization ────────────────────────────────────────────────────

    async def evaluate_tx_authorization(
        self,
        station_id: uuid.UUID,
        frequency_hz: float,
        power_dbm: float,
        mission_rf_profile_id: Optional[uuid.UUID] = None,
    ) -> RegulatoryCheckResult:
        """Composite TX gate. All checks must pass for authorization."""
        station = await self._get_station(station_id)
        checks: List[RegulatoryCheck] = []

        # 1. Certification
        cert = await self._get_certification(station_id)
        checks.append(
            RegulatoryCheck(
                rule="station.certified",
                passed=cert.current_state == "CERTIFIED",
                detail=f"Current certification state: {cert.current_state}",
            )
        )

        # 2. TX switch
        checks.append(
            RegulatoryCheck(
                rule="station.tx_enabled",
                passed=bool(station.tx_enabled),
                detail="tx_enabled is false",
            )
        )

        # 3. Capability band coverage
        caps = (
            await self.db.execute(
                select(StationCapability).where(
                    StationCapability.station_id == station_id,
                    StationCapability.tx_authorized == True,  # noqa: E712
                )
            )
        ).scalars().all()
        cap_ok = any(c.frequency_min_hz <= frequency_hz <= c.frequency_max_hz for c in caps)
        cap_power = min((c.max_tx_power_dbm for c in caps if c.max_tx_power_dbm is not None), default=None)
        checks.append(
            RegulatoryCheck(
                rule="frequency.in_capability",
                passed=cap_ok,
                detail=f"Frequency {frequency_hz} Hz in an authorized station capability band",
            )
        )

        # 4. License validity
        licenses = (
            await self.db.execute(
                select(StationLicense).where(
                    StationLicense.station_id == station_id,
                    StationLicense.status.in_(["valid"]),
                )
            )
        ).scalars().all()
        license_ok = False
        license_power: Optional[float] = None
        for lic in licenses:
            bands = lic.frequency_bands or []
            in_band = any(
                (isinstance(b, dict) and b.get("min_hz", 0) <= frequency_hz <= b.get("max_hz", float("inf")))
                for b in bands
            ) or not bands
            if in_band and (lic.expires_at is None or lic.expires_at > _now()):
                license_ok = True
                if lic.max_power_dbm is not None:
                    license_power = lic.max_power_dbm
        checks.append(
            RegulatoryCheck(
                rule="license.valid",
                passed=license_ok,
                detail="At least one valid license covers the frequency",
            )
        )

        # 5. Power limits
        allowed_power = None
        if cap_power is not None and license_power is not None:
            allowed_power = min(cap_power, license_power)
        elif cap_power is not None:
            allowed_power = cap_power
        elif license_power is not None:
            allowed_power = license_power
        power_ok = allowed_power is None or power_dbm <= allowed_power
        checks.append(
            RegulatoryCheck(
                rule="power.limit",
                passed=power_ok,
                detail=f"Requested {power_dbm} dBm <= allowed {allowed_power} dBm",
            )
        )

        # 6. Mission profile uplink
        profile_ok = True
        if mission_rf_profile_id:
            profile = await self.db.get(MissionRFProfile, mission_rf_profile_id)
            if profile is None:
                profile_ok = False
            else:
                profile_ok = profile.is_uplink_enabled and abs((profile.uplink_frequency_hz or 0) - frequency_hz) < 1e-6
            checks.append(
                RegulatoryCheck(
                    rule="mission_profile.uplink",
                    passed=profile_ok,
                    detail="Mission RF profile permits uplink at this frequency",
                )
            )

        authorized = all(c.passed for c in checks)
        emit(
            self.db,
            aggregate_type="station",
            aggregate_id=station_id,
            event_type="REGULATORY.TX_CHECK",
            payload={
                "station_id": str(station_id),
                "frequency_hz": frequency_hz,
                "power_dbm": power_dbm,
                "authorized": authorized,
            },
        )
        await self.db.commit()
        return RegulatoryCheckResult(station_id=station_id, authorized=authorized, checks=checks)

    # ── Station twin extras ─────────────────────────────────────────────────

    async def report_time_status(
        self,
        station_id: uuid.UUID,
        sync_status: str,
        offset_ms: float,
        clock_source: str = "ntp",
    ) -> StationTimeStatus:
        station = await self._get_station(station_id)
        row = StationTimeStatus(
            station_id=station.id,
            sync_status=sync_status,
            offset_ms=offset_ms,
            last_sync_at=_now(),
            clock_source=clock_source,
            reported_at=_now(),
        )
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

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
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def heartbeat(self, station_id: uuid.UUID, agent_id: str) -> StationAgentIdentity:
        station = await self._get_station(station_id)
        agent = (
            await self.db.execute(
                select(StationAgentIdentity).where(
                    StationAgentIdentity.station_id == station.id,
                    StationAgentIdentity.agent_id == agent_id,
                )
            )
        ).scalars().first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent identity not found")
        agent.last_heartbeat_at = _now()
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    # ── Helpers ─────────────────────────────────────────────────────────────

    async def _get_station(self, station_id: uuid.UUID) -> GroundStation:
        station = await self.db.get(GroundStation, station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        if station.org_id and station.org_id != self.tenant.org_id:
            raise HTTPException(status_code=404, detail="Station not found")
        return station

    async def _get_certification(self, station_id: uuid.UUID) -> StationCertification:
        cert = (
            await self.db.execute(
                select(StationCertification)
                .where(StationCertification.station_id == station_id)
                .order_by(StationCertification.created_at.desc())
            )
        ).scalars().first()
        if not cert:
            cert = StationCertification(station_id=station_id, current_state="REGISTERED")
            self.db.add(cert)
            await self.db.flush()
        return cert