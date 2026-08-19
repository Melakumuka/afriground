"""
API Routes — Per-org Webhooks (Phase 3.1): register delivery endpoints that
receive signed copies of the org's outbox events. Tenant-scoped.
"""
import secrets
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from models.data import Webhook
from services.tenancy import TenantContext, get_tenant_context, write_audit_log

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])


class WebhookCreateRequest(BaseModel):
    url: str
    events: List[str]
    secret: Optional[str] = None


class WebhookResponse(BaseModel):
    id: uuid.UUID
    url: str
    events: List[str]
    is_active: bool
    created_at: Optional[str]


@router.post("", response_model=WebhookResponse)
async def create_webhook(
    req: WebhookCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("api.manage")
    org_id = tenant.require_org()
    if not req.url.startswith(("https://", "http://")):
        raise HTTPException(status_code=422, detail="url must be absolute http(s)")

    webhook = Webhook(
        org_id=org_id,
        url=req.url,
        secret=req.secret or secrets.token_hex(32),
        events=req.events,
        is_active=True,
    )
    db.add(webhook)
    await db.flush()
    await write_audit_log(db, tenant, "webhook.create", "webhook", webhook.id)
    await db.commit()
    await db.refresh(webhook)
    return WebhookResponse(
        id=webhook.id,
        url=webhook.url,
        events=webhook.events or [],
        is_active=webhook.is_active,
        created_at=webhook.created_at.isoformat() if webhook.created_at else None,
    )


@router.get("", response_model=list[WebhookResponse])
async def list_webhooks(
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("api.manage")
    org_id = tenant.require_org()
    rows = (
        await db.execute(
            select(Webhook).where(Webhook.org_id == org_id).order_by(Webhook.created_at.desc())
        )
    ).scalars().all()
    return [
        WebhookResponse(
            id=r.id,
            url=r.url,
            events=r.events or [],
            is_active=r.is_active,
            created_at=r.created_at.isoformat() if r.created_at else None,
        )
        for r in rows
    ]


@router.patch("/{webhook_id}/toggle", response_model=WebhookResponse)
async def toggle_webhook(
    webhook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("api.manage")
    org_id = tenant.require_org()
    row = await db.get(Webhook, webhook_id)
    if not row or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Webhook not found")
    row.is_active = not row.is_active
    await write_audit_log(db, tenant, "webhook.toggle", "webhook", webhook_id)
    await db.commit()
    await db.refresh(row)
    return WebhookResponse(
        id=row.id,
        url=row.url,
        events=row.events or [],
        is_active=row.is_active,
        created_at=row.created_at.isoformat() if row.created_at else None,
    )


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("api.manage")
    org_id = tenant.require_org()
    row = await db.get(Webhook, webhook_id)
    if not row or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Webhook not found")
    await db.delete(row)
    await write_audit_log(db, tenant, "webhook.delete", "webhook", webhook_id)
    await db.commit()
    return {"deleted": True}