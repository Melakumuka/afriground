"""
API Routes — Missions & Spacecraft (Phase 1.2)
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from services.mission_service import (
    MissionService,
    SpacecraftCreate,
    SpacecraftResponse,
    MissionCreate,
    MissionResponse,
    MissionProfileCreate,
    MissionProfileResponse,
    RFProfileCreate,
    RFProfileResponse,
    TMDefinitionCreate,
    TCCommandCreate,
    ConstraintCreate,
    SLACreate,
)
from services.tenancy import TenantContext, get_tenant_context

router = APIRouter(prefix="/api/v1/missions", tags=["Missions & Spacecraft"])


@router.post("/spacecraft", response_model=SpacecraftResponse)
async def create_spacecraft(
    req: SpacecraftCreate,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("mission.manage")
    return await MissionService(db, tenant).create_spacecraft(req)


@router.get("/spacecraft", response_model=list[SpacecraftResponse])
async def list_spacecraft(
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return await MissionService(db, tenant).list_spacecraft()


@router.post("", response_model=MissionResponse)
async def create_mission(
    req: MissionCreate,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("mission.manage")
    return await MissionService(db, tenant).create_mission(req)


@router.get("", response_model=list[MissionResponse])
async def list_missions(
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    return await MissionService(db, tenant).list_missions()


@router.post("/{mission_id}/activate", response_model=MissionResponse)
async def activate_mission(
    mission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("mission.manage")
    return await MissionService(db, tenant).activate_mission(mission_id)


@router.post("/profiles", response_model=MissionProfileResponse)
async def create_profile(
    req: MissionProfileCreate,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("mission.manage")
    return await MissionService(db, tenant).create_profile(req)


@router.post("/rf-profiles", response_model=RFProfileResponse)
async def create_rf_profile(
    req: RFProfileCreate,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("mission.manage")
    return await MissionService(db, tenant).create_rf_profile(req)


@router.post("/telemetry-definitions")
async def create_tm_definition(
    req: TMDefinitionCreate,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("mission.manage")
    return await MissionService(db, tenant).create_tm_definition(req)


@router.post("/telecommands")
async def create_tc_command(
    req: TCCommandCreate,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("mission.manage")
    return await MissionService(db, tenant).create_tc_command(req)


@router.post("/constraints")
async def create_constraint(
    req: ConstraintCreate,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("mission.manage")
    return await MissionService(db, tenant).create_constraint(req)


@router.post("/slas")
async def create_sla(
    req: SLACreate,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("mission.manage")
    return await MissionService(db, tenant).create_sla(req)