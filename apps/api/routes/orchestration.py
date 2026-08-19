"""
API Routes — Orchestration Runtime (Phase 2.0): outbox health/backpressure.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from services.orchestration_runtime import metrics
from services.tenancy import TenantContext, get_tenant_context

router = APIRouter(prefix="/api/v1/orchestration", tags=["Orchestration"])


@router.get("/metrics")
async def orchestration_metrics(
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("platform.admin")
    return await metrics(db)