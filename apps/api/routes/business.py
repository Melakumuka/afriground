"""
API Routes — Business tier (Phase 3.0): SLA violations, contract usage,
recurring mission auto-booking triggers. Tenant-scoped.
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from models.core import Contract
from services.commercial_engine import CommercialEngine
from services.sla import SLAService
from services.tenancy import TenantContext, get_tenant_context, write_audit_log

router = APIRouter(prefix="/api/v1/business", tags=["Business"])


class ContractUsageResponse(BaseModel):
    contract_id: uuid.UUID
    org_id: uuid.UUID
    reserved_capacity_minutes: int
    used_minutes: int
    remaining_minutes: int
    utilization_pct: float


class SLAViolationResponse(BaseModel):
    id: uuid.UUID
    mission_id: uuid.UUID
    observation_job_id: uuid.UUID
    sla_type: str
    target_value: float
    actual_value: float
    unit: Optional[str]
    status: str
    violated_at: str


@router.get("/contracts", response_model=list[dict])
async def list_contracts(
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """List contracts for the tenant."""
    from sqlalchemy import select
    result = await db.execute(select(Contract).where(Contract.org_id == tenant.org_id))
    return [{"id": c.id, "org_id": c.org_id, "start_date": c.start_date, "end_date": c.end_date, "status": c.status, "service_tier": c.service_tier} for c in result.scalars().all()]



@router.get("/contracts/{contract_id}/usage", response_model=ContractUsageResponse)
async def contract_usage(
    contract_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Real reserved-capacity utilization for a contract (minutes on air)."""
    contract = await db.get(Contract, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if contract.org_id != tenant.org_id:
        tenant.require_permission("platform.admin")

    detail = await CommercialEngine(db).get_contract_usage(contract_id)
    utilization = (
        round(detail.used_minutes / detail.reserved_capacity_minutes * 100, 1)
        if detail.reserved_capacity_minutes > 0
        else 0.0
    )
    await write_audit_log(
        db, tenant, "business.contract.usage", "contract", contract_id
    )
    await db.commit()
    return ContractUsageResponse(
        contract_id=contract_id,
        org_id=contract.org_id,
        reserved_capacity_minutes=detail.reserved_capacity_minutes,
        used_minutes=detail.used_minutes,
        remaining_minutes=detail.remaining_minutes,
        utilization_pct=utilization,
    )


@router.get("/sla-violations", response_model=list[SLAViolationResponse])
async def sla_violations(
    mission_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """List SLA breaches. Platform admins see the whole network; others see
    their own org's jobs only."""
    tenant.require_permission("platform.admin")
    rows = await SLAService(db).list_violations(
        org_id=tenant.org_id,
        mission_id=mission_id,
        status=status,
        limit=limit,
    )
    return [
        SLAViolationResponse(
            id=r.id,
            mission_id=r.mission_id,
            observation_job_id=r.observation_job_id,
            sla_type=r.sla_type,
            target_value=r.target_value,
            actual_value=r.actual_value,
            unit=r.unit,
            status=r.status,
            violated_at=r.violated_at.isoformat(),
        )
        for r in rows
    ]


@router.post("/recurring-missions/trigger-booking")
async def trigger_recurring_booking(
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    """Manually run the recurring-mission booking sweep for the org (the Celery
    beat task does this automatically)."""
    tenant.require_org()
    from services.commercial_engine import RecurringMissionSweeper

    created = await RecurringMissionSweeper(db).sweep(tenant.org_id)
    await write_audit_log(
        db, tenant, "business.recurring.sweep", "recurring_mission",
        details={"created_bookings": created},
    )
    await db.commit()
    return {"created_bookings": created}