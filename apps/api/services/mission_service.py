"""
Mission Service — CRUD and schemas for spacecraft, missions, profiles, RF,
TM/TC definitions, constraints, and SLAs. Phase 1.2.
"""
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.mission import (
    Spacecraft,
    Mission,
    MissionProfile,
    MissionRFProfile,
    MissionTelemetryDefinition,
    MissionTelecommandDefinition,
    MissionOperationalConstraint,
    MissionSLA,
)
from models.spacecraft import Satellite
from services.tenancy import TenantContext, write_audit_log


# ── Schemas ─────────────────────────────────────────────────────────────────

class SpacecraftCreate(BaseModel):
    name: str
    norad_id: Optional[int] = None
    satellite_id: Optional[uuid.UUID] = None
    owner_org_id: Optional[uuid.UUID] = None
    spacecraft_metadata: Optional[dict] = None


class SpacecraftResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    name: str
    norad_id: Optional[int]
    status: str


class MissionCreate(BaseModel):
    spacecraft_id: uuid.UUID
    name: str
    description: Optional[str] = None
    mission_type: str = "earth_observation"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class MissionResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    spacecraft_id: uuid.UUID
    name: str
    mission_type: str
    status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]


class MissionProfileCreate(BaseModel):
    mission_id: uuid.UUID
    name: str
    version: str = "1.0"
    profile_metadata: Optional[dict] = None


class MissionProfileResponse(BaseModel):
    id: uuid.UUID
    mission_id: uuid.UUID
    name: str
    version: str
    is_active: bool


class RFProfileCreate(BaseModel):
    mission_profile_id: uuid.UUID
    band: str
    uplink_frequency_hz: Optional[float] = None
    downlink_frequency_hz: Optional[float] = None
    uplink_modulation: Optional[str] = None
    downlink_modulation: Optional[str] = None
    symbol_rate: Optional[float] = None
    polarization: Optional[str] = None
    max_tx_power_dbm: Optional[float] = None
    is_uplink_enabled: bool = False


class RFProfileResponse(BaseModel):
    id: uuid.UUID
    mission_profile_id: uuid.UUID
    band: str
    uplink_frequency_hz: Optional[float]
    downlink_frequency_hz: Optional[float]
    is_uplink_enabled: bool


class TMDefinitionCreate(BaseModel):
    mission_profile_id: uuid.UUID
    name: str
    parameter_id: str
    data_type: str = "float32"
    unit: Optional[str] = None
    bit_offset: Optional[int] = None
    bit_length: Optional[int] = None
    scaling_factor: float = 1.0
    scaling_offset: float = 0.0


class TCCommandCreate(BaseModel):
    mission_profile_id: uuid.UUID
    name: str
    command_code: str
    parameters: Optional[dict] = None
    constraints: Optional[dict] = None


class ConstraintCreate(BaseModel):
    mission_id: uuid.UUID
    constraint_type: str
    value: Optional[dict] = None
    is_active: bool = True


class SLACreate(BaseModel):
    mission_id: uuid.UUID
    sla_type: str
    target_value: float
    unit: str = "percent"
    reporting_window_days: int = 30


# ── Service ─────────────────────────────────────────────────────────────────

class MissionService:
    def __init__(self, db: AsyncSession, tenant: TenantContext):
        self.db = db
        self.tenant = tenant

    # ── Spacecraft ──────────────────────────────────────────────────────────

    async def create_spacecraft(self, req: SpacecraftCreate) -> SpacecraftResponse:
        if req.satellite_id:
            sat = await self.db.get(Satellite, req.satellite_id)
            if not sat:
                raise HTTPException(status_code=404, detail="Referenced satellite not found")

        sc = Spacecraft(
            org_id=self.tenant.org_id,
            satellite_id=req.satellite_id,
            name=req.name,
            norad_id=req.norad_id,
            owner_org_id=req.owner_org_id or self.tenant.org_id,
            spacecraft_metadata=req.spacecraft_metadata or {},
            status="operational",
        )
        self.db.add(sc)
        await self.db.commit()
        await self.db.refresh(sc)
        return SpacecraftResponse(id=sc.id, org_id=sc.org_id, name=sc.name, norad_id=sc.norad_id, status=sc.status)

    async def list_spacecraft(self) -> List[SpacecraftResponse]:
        stmt = select(Spacecraft).where(Spacecraft.org_id == self.tenant.org_id)
        rows = (await self.db.execute(stmt)).scalars().all()
        return [
            SpacecraftResponse(id=s.id, org_id=s.org_id, name=s.name, norad_id=s.norad_id, status=s.status)
            for s in rows
        ]

    # ── Missions ────────────────────────────────────────────────────────────

    async def create_mission(self, req: MissionCreate) -> MissionResponse:
        sc = await self.db.get(Spacecraft, req.spacecraft_id)
        if not sc or sc.org_id != self.tenant.org_id:
            raise HTTPException(status_code=404, detail="Spacecraft not found")

        mission = Mission(
            org_id=self.tenant.org_id,
            spacecraft_id=req.spacecraft_id,
            name=req.name,
            description=req.description,
            mission_type=req.mission_type,
            start_date=req.start_date,
            end_date=req.end_date,
            status="draft",
        )
        self.db.add(mission)
        await self.db.commit()
        await self.db.refresh(mission)
        await write_audit_log(
            self.db,
            self.tenant,
            action="mission.create",
            resource_type="mission",
            resource_id=mission.id,
        )
        await self.db.commit()
        return MissionResponse(
            id=mission.id,
            org_id=mission.org_id,
            spacecraft_id=mission.spacecraft_id,
            name=mission.name,
            mission_type=mission.mission_type,
            status=mission.status,
            start_date=mission.start_date,
            end_date=mission.end_date,
        )

    async def list_missions(self) -> List[MissionResponse]:
        stmt = select(Mission).where(Mission.org_id == self.tenant.org_id)
        rows = (await self.db.execute(stmt)).scalars().all()
        return [
            MissionResponse(
                id=m.id, org_id=m.org_id, spacecraft_id=m.spacecraft_id, name=m.name,
                mission_type=m.mission_type, status=m.status,
                start_date=m.start_date, end_date=m.end_date,
            )
            for m in rows
        ]

    async def activate_mission(self, mission_id: uuid.UUID) -> MissionResponse:
        mission = await self._get_mission(mission_id)
        mission.status = "active"
        await self.db.commit()
        await self.db.refresh(mission)
        return MissionResponse(
            id=mission.id, org_id=mission.org_id, spacecraft_id=mission.spacecraft_id,
            name=mission.name, mission_type=mission.mission_type, status=mission.status,
            start_date=mission.start_date, end_date=mission.end_date,
        )

    # ── Mission profiles ────────────────────────────────────────────────────

    async def create_profile(self, req: MissionProfileCreate) -> MissionProfileResponse:
        await self._get_mission(req.mission_id)
        profile = MissionProfile(
            mission_id=req.mission_id,
            name=req.name,
            version=req.version,
            profile_metadata=req.profile_metadata or {},
            is_active=True,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return MissionProfileResponse(
            id=profile.id, mission_id=profile.mission_id, name=profile.name,
            version=profile.version, is_active=profile.is_active,
        )

    async def list_profiles(self, mission_id: uuid.UUID) -> List[MissionProfileResponse]:
        await self._get_mission(mission_id)
        stmt = select(MissionProfile).where(MissionProfile.mission_id == mission_id)
        rows = (await self.db.execute(stmt)).scalars().all()
        return [
            MissionProfileResponse(
                id=p.id, mission_id=p.mission_id, name=p.name,
                version=p.version, is_active=p.is_active,
            )
            for p in rows
        ]

    async def create_rf_profile(self, req: RFProfileCreate) -> RFProfileResponse:
        profile = await self.db.get(MissionProfile, req.mission_profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Mission profile not found")

        rf = MissionRFProfile(
            mission_profile_id=req.mission_profile_id,
            band=req.band,
            uplink_frequency_hz=req.uplink_frequency_hz,
            downlink_frequency_hz=req.downlink_frequency_hz,
            uplink_modulation=req.uplink_modulation,
            downlink_modulation=req.downlink_modulation,
            symbol_rate=req.symbol_rate,
            polarization=req.polarization,
            max_tx_power_dbm=req.max_tx_power_dbm,
            is_uplink_enabled=req.is_uplink_enabled,
            is_active=True,
        )
        self.db.add(rf)
        await self.db.commit()
        await self.db.refresh(rf)
        return RFProfileResponse(
            id=rf.id, mission_profile_id=rf.mission_profile_id, band=rf.band,
            uplink_frequency_hz=rf.uplink_frequency_hz, downlink_frequency_hz=rf.downlink_frequency_hz,
            is_uplink_enabled=rf.is_uplink_enabled,
        )

    async def create_tm_definition(self, req: TMDefinitionCreate):
        profile = await self.db.get(MissionProfile, req.mission_profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Mission profile not found")
        tm = MissionTelemetryDefinition(**req.model_dump())
        self.db.add(tm)
        await self.db.commit()
        await self.db.refresh(tm)
        return tm

    async def create_tc_command(self, req: TCCommandCreate):
        profile = await self.db.get(MissionProfile, req.mission_profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Mission profile not found")
        tc = MissionTelecommandDefinition(**req.model_dump())
        self.db.add(tc)
        await self.db.commit()
        await self.db.refresh(tc)
        return tc

    async def create_constraint(self, req: ConstraintCreate):
        await self._get_mission(req.mission_id)
        constraint = MissionOperationalConstraint(**req.model_dump())
        self.db.add(constraint)
        await self.db.commit()
        await self.db.refresh(constraint)
        return constraint

    async def create_sla(self, req: SLACreate):
        await self._get_mission(req.mission_id)
        sla = MissionSLA(**req.model_dump())
        self.db.add(sla)
        await self.db.commit()
        await self.db.refresh(sla)
        return sla

    # ── Helpers ─────────────────────────────────────────────────────────────

    async def _get_mission(self, mission_id: uuid.UUID) -> Mission:
        mission = await self.db.get(Mission, mission_id)
        if not mission or mission.org_id != self.tenant.org_id:
            raise HTTPException(status_code=404, detail="Mission not found")
        return mission