"""
API Routes — API Keys (Phase 3.1): programmatic access key management.
Tenant-scoped; key creation requires api.manage.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from services import api_keys
from services.tenancy import TenantContext, get_tenant_context, write_audit_log

router = APIRouter(prefix="/api/v1/keys", tags=["API Keys"])


class KeyCreateRequest(BaseModel):
    name: str = "default"
    scopes: List[str] = []
    rate_limit_tier: str = "standard"


class KeyCreateResponse(BaseModel):
    id: uuid.UUID
    name: str
    scopes: List[str]
    rate_limit_tier: str
    api_key: str  # plaintext, shown once


class KeyListResponse(BaseModel):
    id: uuid.UUID
    name: str
    scopes: List[str]
    rate_limit_tier: str
    is_active: bool
    created_at: Optional[str]


class KeyMeResponse(BaseModel):
    org_id: uuid.UUID
    key_id: uuid.UUID
    scopes: List[str]


@router.post("", response_model=KeyCreateResponse)
async def create_key(
    req: KeyCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("api.manage")
    org_id = tenant.require_org()
    row, plaintext = api_keys.generate_api_key(
        db, org_id, name=req.name, scopes=req.scopes, tier=req.rate_limit_tier
    )
    await write_audit_log(db, tenant, "api_key.create", "api_key", row.id)
    await db.commit()
    return KeyCreateResponse(
        id=row.id,
        name=row.name,
        scopes=row.scopes or [],
        rate_limit_tier=row.rate_limit_tier,
        api_key=plaintext,
    )


@router.get("", response_model=list[KeyListResponse])
async def list_keys(
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("api.manage")
    org_id = tenant.require_org()
    rows = await api_keys.list_api_keys(db, org_id)
    return [
        KeyListResponse(
            id=r.id,
            name=r.name,
            scopes=r.scopes or [],
            rate_limit_tier=r.rate_limit_tier,
            is_active=r.is_active,
            created_at=r.created_at.isoformat() if r.created_at else None,
        )
        for r in rows
    ]


@router.delete("/{key_id}")
async def revoke_key(
    key_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("api.manage")
    org_id = tenant.require_org()
    if not await api_keys.revoke_api_key(db, key_id, org_id):
        raise HTTPException(status_code=404, detail="API key not found")
    await write_audit_log(db, tenant, "api_key.revoke", "api_key", key_id)
    await db.commit()
    return {"revoked": True}


@router.get("/me", response_model=KeyMeResponse)
async def key_me(
    db: AsyncSession = Depends(get_db_session),
    ctx: dict = Depends(api_keys.get_api_key_context),
):
    """Programmatic access: echo the authenticated key context."""
    return KeyMeResponse(
        org_id=ctx["org_id"],
        key_id=ctx["key_id"],
        scopes=ctx["scopes"],
    )