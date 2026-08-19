"""
API Routes — Network Operations (Phase 3.2): station routing ranking and
opportunity selection across the multi-station network.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from services.network_routing import NetworkRoutingService
from services.tenancy import TenantContext, get_tenant_context

router = APIRouter(prefix="/api/v1/network", tags=["Network Routing"])


@router.get("/ranking")
async def network_ranking(
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("platform.admin")
    return await NetworkRoutingService(db).rank_network()