"""
API Routes — Regulatory Enforcement (Phase 1.5)
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from services.regulatory import RegulatoryAuthorizationService
from services.tenancy import TenantContext, get_tenant_context

router = APIRouter(prefix="/api/v1/regulatory", tags=["Regulatory"])


@router.post("/stations/register")
async def register_station(
    code: str,
    name: str,
    country: str,
    latitude: float,
    longitude: float,
    altitude_m: float,
    operator_contact_email: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("station.manage")
    service = RegulatoryAuthorizationService(db, tenant)
    station = await service.register_station(
        code, name, country, latitude, longitude, altitude_m, operator_contact_email
    )
    return {
        "id": str(station.id),
        "code": station.code,
        "name": station.name,
        "country": station.country,
        "certification_state": station.certification_state,
        "tx_enabled": station.tx_enabled,
        "registration_date": station.registration_date,
    }


@router.post("/stations/{station_id}/certification")
async def transition_certification(
    station_id: uuid.UUID,
    to_state: str,
    reason: str = "",
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("station.certify")
    service = RegulatoryAuthorizationService(db, tenant)
    cert = await service.transition_certification(station_id, to_state.upper(), reason)
    return {
        "id": str(cert.id),
        "station_id": str(cert.station_id),
        "current_state": cert.current_state,
        "cert_version": cert.cert_version,
        "certified_at": cert.certified_at,
    }


@router.post("/stations/{station_id}/tx/authorize")
async def evaluate_tx(
    station_id: uuid.UUID,
    frequency_hz: float,
    power_dbm: float,
    mission_rf_profile_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    service = RegulatoryAuthorizationService(db, tenant)
    result = await service.evaluate_tx_authorization(
        station_id, frequency_hz, power_dbm, mission_rf_profile_id
    )
    return result.model_dump()


@router.post("/stations/{station_id}/time-status")
async def report_time_status(
    station_id: uuid.UUID,
    sync_status: str,
    offset_ms: float,
    clock_source: str = "ntp",
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    service = RegulatoryAuthorizationService(db, tenant)
    row = await service.report_time_status(station_id, sync_status, offset_ms, clock_source)
    return {
        "id": str(row.id),
        "station_id": str(row.station_id),
        "sync_status": row.sync_status,
        "offset_ms": row.offset_ms,
        "last_sync_at": row.last_sync_at,
    }


@router.post("/stations/{station_id}/agents/heartbeat")
async def agent_heartbeat(
    station_id: uuid.UUID,
    agent_id: str,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    service = RegulatoryAuthorizationService(db, tenant)
    agent = await service.heartbeat(station_id, agent_id)
    return {
        "id": str(agent.id),
        "station_id": str(agent.station_id),
        "agent_id": agent.agent_id,
        "last_heartbeat_at": agent.last_heartbeat_at,
        "status": agent.status,
    }