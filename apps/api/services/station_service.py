"""
Station Service — digital twin CRUD: capabilities, hardware, licenses,
certifications, quality scores, time status, and agent identity. Phase 1.3.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.station import GroundStation
from models.station_twin import (
    StationCapability,
    StationHardware,
    StationLicense,
    StationCertification,
    StationCertificationEvent,
    StationQualityScore,
    StationTimeStatus,
    StationAgentIdentity,
)
from services.tenancy import TenantContext, write_audit_log


# ── Schemas ─────────────────────────────────────────────────────────────────

class CapabilityCreate(BaseModel):
    station_id: uuid.UUID
    band: str
    frequency_min_hz: float
    frequency_max_hz: float
    polarization: Optional[str] = None
    max_tx_power_dbm: Optional[float] = None
    tx_authorized: bool = False
    gain_dbi: Optional[float] = None
    noise_figure_db: Optional[float] = None
    notes: Optional[str] = None


class HardwareCreate(BaseModel):
    station_id: uuid.UUID
    hardware_type: str
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    status: str = "operational"
    installed_at: Optional[datetime] = None


class LicenseCreate(BaseModel):
    station_id: uuid.UUID
    license_type: str
    issuing_authority: str
    license_number: Optional[str] = None
    country: Optional[str] = None
    frequency_bands: Optional[list] = None
    max_power_dbm: Optional[float] = None
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class StationResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    country: str
    latitude: float
    longitude: float
    altitude_m: float
    status: str
    certification_state: str
    tx_enabled: bool


class CapabilityResponse(BaseModel):
    id: uuid.UUID
    station_id: uuid.UUID
    band: str
    frequency_min_hz: float
    frequency_max_hz: float
    max_tx_power_dbm: Optional[float]
    tx_authorized: bool
    gain_dbi: Optional[float]


class LicenseResponse(BaseModel):
    id: uuid.UUID
    station_id: uuid.UUID
    license_type: str
    issuing_authority: str
    license_number: Optional[str]
    country: Optional[str]
    frequency_bands: Optional[list]
    max_power_dbm: Optional[float]
    expires_at: Optional[datetime]
    status: str


class CertificationResponse(BaseModel):
    id: uuid.UUID
    station_id: uuid.UUID
    current_state: str
    cert_version: str
    certified_at: Optional[datetime]


class CertificationEventResponse(BaseModel):
    id: uuid.UUID
    station_id: uuid.UUID
    from_state: Optional[str]
    to_state: str
    transition_reason: Optional[str]
    created_at: Optional[datetime]


# ── Service ─────────────────────────────────────────────────────────────────

class StationService:
    def __init__(self, db: AsyncSession, tenant: TenantContext):
        self.db = db
        self.tenant = tenant

    async def get_station(self, station_id: uuid.UUID) -> StationResponse:
        station = await self._get_station(station_id)
        return StationResponse(
            id=station.id, name=station.name, code=station.code, country=station.country,
            latitude=station.latitude, longitude=station.longitude, altitude_m=station.altitude_m,
            status=station.status, certification_state=station.certification_state,
            tx_enabled=station.tx_enabled,
        )

    async def list_stations(self) -> List[StationResponse]:
        stmt = select(GroundStation).where(GroundStation.org_id == self.tenant.org_id)
        rows = (await self.db.execute(stmt)).scalars().all()
        return [
            StationResponse(
                id=s.id, name=s.name, code=s.code, country=s.country,
                latitude=s.latitude, longitude=s.longitude, altitude_m=s.altitude_m,
                status=s.status, certification_state=s.certification_state, tx_enabled=s.tx_enabled,
            )
            for s in rows
        ]

    async def set_tx_enabled(self, station_id: uuid.UUID, enabled: bool) -> StationResponse:
        station = await self._get_station(station_id)
        station.tx_enabled = enabled
        await self.db.commit()
        await self.db.refresh(station)
        return await self.get_station(station_id)

    # ── Capabilities ────────────────────────────────────────────────────────

    async def add_capability(self, req: CapabilityCreate) -> CapabilityResponse:
        await self._get_station(req.station_id)
        cap = StationCapability(
            station_id=req.station_id,
            band=req.band,
            frequency_min_hz=req.frequency_min_hz,
            frequency_max_hz=req.frequency_max_hz,
            polarization=req.polarization,
            max_tx_power_dbm=req.max_tx_power_dbm,
            tx_authorized=req.tx_authorized,
            gain_dbi=req.gain_dbi,
            noise_figure_db=req.noise_figure_db,
            notes=req.notes,
        )
        self.db.add(cap)
        await self.db.commit()
        await self.db.refresh(cap)
        return CapabilityResponse(
            id=cap.id, station_id=cap.station_id, band=cap.band,
            frequency_min_hz=cap.frequency_min_hz, frequency_max_hz=cap.frequency_max_hz,
            max_tx_power_dbm=cap.max_tx_power_dbm, tx_authorized=cap.tx_authorized,
            gain_dbi=cap.gain_dbi,
        )

    async def list_capabilities(self, station_id: uuid.UUID) -> List[CapabilityResponse]:
        await self._get_station(station_id)
        stmt = select(StationCapability).where(StationCapability.station_id == station_id)
        rows = (await self.db.execute(stmt)).scalars().all()
        return [
            CapabilityResponse(
                id=c.id, station_id=c.station_id, band=c.band,
                frequency_min_hz=c.frequency_min_hz, frequency_max_hz=c.frequency_max_hz,
                max_tx_power_dbm=c.max_tx_power_dbm, tx_authorized=c.tx_authorized,
                gain_dbi=c.gain_dbi,
            )
            for c in rows
        ]

    # ── Hardware ────────────────────────────────────────────────────────────

    async def add_hardware(self, req: HardwareCreate) -> StationHardware:
        await self._get_station(req.station_id)
        hw = StationHardware(**req.model_dump())
        self.db.add(hw)
        await self.db.commit()
        await self.db.refresh(hw)
        return hw

    async def list_hardware(self, station_id: uuid.UUID) -> List[StationHardware]:
        await self._get_station(station_id)
        stmt = select(StationHardware).where(StationHardware.station_id == station_id)
        rows = (await self.db.execute(stmt)).scalars().all()
        return list(rows)

    # ── Licenses ────────────────────────────────────────────────────────────

    async def add_license(self, req: LicenseCreate) -> LicenseResponse:
        await self._get_station(req.station_id)
        lic = StationLicense(
            station_id=req.station_id,
            license_type=req.license_type,
            issuing_authority=req.issuing_authority,
            license_number=req.license_number,
            country=req.country,
            frequency_bands=req.frequency_bands or [],
            max_power_dbm=req.max_power_dbm,
            issued_at=req.issued_at,
            expires_at=req.expires_at,
            status="valid",
        )
        self.db.add(lic)
        await self.db.commit()
        await self.db.refresh(lic)
        return LicenseResponse(
            id=lic.id, station_id=lic.station_id, license_type=lic.license_type,
            issuing_authority=lic.issuing_authority, license_number=lic.license_number,
            country=lic.country, frequency_bands=lic.frequency_bands,
            max_power_dbm=lic.max_power_dbm, expires_at=lic.expires_at, status=lic.status,
        )

    async def list_licenses(self, station_id: uuid.UUID) -> List[LicenseResponse]:
        await self._get_station(station_id)
        stmt = select(StationLicense).where(StationLicense.station_id == station_id)
        rows = (await self.db.execute(stmt)).scalars().all()
        return [
            LicenseResponse(
                id=l.id, station_id=l.station_id, license_type=l.license_type,
                issuing_authority=l.issuing_authority, license_number=l.license_number,
                country=l.country, frequency_bands=l.frequency_bands,
                max_power_dbm=l.max_power_dbm, expires_at=l.expires_at, status=l.status,
            )
            for l in rows
        ]

    # ── Certification history ───────────────────────────────────────────────

    async def get_certification(self, station_id: uuid.UUID) -> CertificationResponse:
        await self._get_station(station_id)
        cert = (
            await self.db.execute(
                select(StationCertification)
                .where(StationCertification.station_id == station_id)
                .order_by(StationCertification.created_at.desc())
            )
        ).scalars().first()
        if not cert:
            raise HTTPException(status_code=404, detail="No certification record for station")
        return CertificationResponse(
            id=cert.id, station_id=cert.station_id, current_state=cert.current_state,
            cert_version=cert.cert_version, certified_at=cert.certified_at,
        )

    async def list_certification_events(self, station_id: uuid.UUID) -> List[CertificationEventResponse]:
        await self._get_station(station_id)
        stmt = (
            select(StationCertificationEvent)
            .where(StationCertificationEvent.station_id == station_id)
            .order_by(StationCertificationEvent.created_at)
        )
        rows = (await self.db.execute(stmt)).scalars().all()
        return [
            CertificationEventResponse(
                id=e.id, station_id=e.station_id, from_state=e.from_state,
                to_state=e.to_state, transition_reason=e.transition_reason, created_at=e.created_at,
            )
            for e in rows
        ]

    # ── Quality / time / agent ──────────────────────────────────────────────

    async def add_quality_score(self, station_id: uuid.UUID, score: float, availability: float = 0.0,
                                reliability: float = 0.0, timeliness: float = 0.0) -> StationQualityScore:
        await self._get_station(station_id)
        row = StationQualityScore(
            station_id=station_id, score=score, availability=availability,
            reliability=reliability, timeliness=timeliness,
        )
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def list_time_statuses(self, station_id: uuid.UUID) -> List[StationTimeStatus]:
        await self._get_station(station_id)
        stmt = (
            select(StationTimeStatus)
            .where(StationTimeStatus.station_id == station_id)
            .order_by(StationTimeStatus.reported_at.desc())
        )
        rows = (await self.db.execute(stmt)).scalars().all()
        return list(rows)

    async def list_agents(self, station_id: uuid.UUID) -> List[StationAgentIdentity]:
        await self._get_station(station_id)
        stmt = select(StationAgentIdentity).where(StationAgentIdentity.station_id == station_id)
        rows = (await self.db.execute(stmt)).scalars().all()
        return list(rows)

    # ── Helpers ─────────────────────────────────────────────────────────────

    async def _get_station(self, station_id: uuid.UUID) -> GroundStation:
        station = await self.db.get(GroundStation, station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")
        if station.org_id and station.org_id != self.tenant.org_id:
            raise HTTPException(status_code=404, detail="Station not found")
        return station