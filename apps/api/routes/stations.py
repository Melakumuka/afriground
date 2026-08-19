"""
API Routes — Station Digital Twin (Phase 1.3)
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from services.regulatory import RegulatoryAuthorizationService
from services.station_service import (
    StationService,
    StationResponse,
    CapabilityCreate,
    CapabilityResponse,
    HardwareCreate,
    LicenseCreate,
    LicenseResponse,
    CertificationResponse,
    CertificationEventResponse,
)
from services.tenancy import TenantContext, get_tenant_context

router = APIRouter(prefix="/api/v1/stations", tags=["Station Digital Twin"])


@router.get("", response_model=list[StationResponse])
async def list_stations(
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return await StationService(db, tenant).list_stations()


@router.get("/{station_id}", response_model=StationResponse)
async def get_station(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return await StationService(db, tenant).get_station(station_id)


@router.post("/{station_id}/tx", response_model=StationResponse)
async def set_tx_enabled(
    station_id: uuid.UUID,
    enabled: bool,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("station.manage")
    return await StationService(db, tenant).set_tx_enabled(station_id, enabled)


@router.post("/{station_id}/capabilities", response_model=CapabilityResponse)
async def add_capability(
    station_id: uuid.UUID,
    req: CapabilityCreate,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("station.manage")
    req.station_id = station_id
    return await StationService(db, tenant).add_capability(req)


@router.get("/{station_id}/capabilities", response_model=list[CapabilityResponse])
async def list_capabilities(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return await StationService(db, tenant).list_capabilities(station_id)


@router.post("/{station_id}/hardware")
async def add_hardware(
    station_id: uuid.UUID,
    req: HardwareCreate,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("station.manage")
    req.station_id = station_id
    return await StationService(db, tenant).add_hardware(req)


@router.get("/{station_id}/hardware")
async def list_hardware(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return await StationService(db, tenant).list_hardware(station_id)


@router.post("/{station_id}/licenses", response_model=LicenseResponse)
async def add_license(
    station_id: uuid.UUID,
    req: LicenseCreate,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("station.manage")
    req.station_id = station_id
    return await StationService(db, tenant).add_license(req)


@router.get("/{station_id}/licenses", response_model=list[LicenseResponse])
async def list_licenses(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return await StationService(db, tenant).list_licenses(station_id)


@router.get("/{station_id}/certification", response_model=CertificationResponse)
async def get_certification(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return await StationService(db, tenant).get_certification(station_id)


@router.get("/{station_id}/certification/events", response_model=list[CertificationEventResponse])
async def list_certification_events(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return await StationService(db, tenant).list_certification_events(station_id)


@router.post("/{station_id}/quality-scores")
async def add_quality_score(
    station_id: uuid.UUID,
    score: float,
    availability: float = 0.0,
    reliability: float = 0.0,
    timeliness: float = 0.0,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("station.manage")
    return await StationService(db, tenant).add_quality_score(station_id, score, availability, reliability, timeliness)


@router.get("/{station_id}/time-status")
async def list_time_statuses(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return await StationService(db, tenant).list_time_statuses(station_id)


@router.get("/{station_id}/agents")
async def list_agents(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return await StationService(db, tenant).list_agents(station_id)


@router.post("/{station_id}/agents")
async def register_agent(
    station_id: uuid.UUID,
    agent_id: str,
    agent_version: str = "",
    public_key_pem: str = "",
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("station.manage")
    return await RegulatoryAuthorizationService(db, tenant).register_agent(
        station_id, agent_id, agent_version, public_key_pem
    )