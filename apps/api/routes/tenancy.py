"""
API Routes — Tenancy & RBAC (Phase 1.1)
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db_session
from models.core import Organization, Role, User
from models.tenancy import AuditLog, Permission, RolePermission
from services.tenancy import TenantContext, get_tenant_context, write_audit_log

router = APIRouter(prefix="/api/v1/tenancy", tags=["Tenancy & RBAC"])


@router.get("/me")
async def my_tenant(tenant: TenantContext = Depends(get_tenant_context)):
    return {
        "user_id": str(tenant.user.id),
        "email": tenant.user.email,
        "organization": {
            "id": str(tenant.organization.id) if tenant.organization else None,
            "name": tenant.organization.name if tenant.organization else None,
            "slug": tenant.organization.slug if tenant.organization else None,
        },
        "roles": [{"id": str(r.id), "name": r.name} for r in tenant.roles],
        "permissions": sorted(tenant.permissions),
    }


@router.get("/permissions")
async def list_permissions(
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    rows = (await db.execute(select(Permission).order_by(Permission.code))).scalars().all()
    return [{"id": str(p.id), "code": p.code, "name": p.name} for p in rows]


@router.get("/roles")
async def list_roles(
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    rows = (await db.execute(select(Role).order_by(Role.name))).scalars().all()
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "description": r.description,
            "is_system": r.is_system,
            "permissions": await _role_permissions(db, r.id),
        }
        for r in rows
    ]


@router.post("/roles/{role_id}/permissions")
async def grant_permission(
    role_id: uuid.UUID,
    permission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
):
    tenant.require_permission("rbac.manage")
    role = await db.get(Role, role_id)
    permission = await db.get(Permission, permission_id)
    if not role or not permission:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Role or permission not found")
    db.add(RolePermission(role_id=role_id, permission_id=permission_id))
    await write_audit_log(
        db, tenant,
        action="rbac.grant_permission",
        resource_type="role",
        resource_id=role_id,
        details={"permission_id": str(permission_id)},
    )
    await db.commit()
    return {"granted": True, "role_id": str(role_id), "permission_id": str(permission_id)}


@router.get("/audit-logs")
async def list_audit_logs(
    db: AsyncSession = Depends(get_db_session),
    tenant: TenantContext = Depends(get_tenant_context),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    tenant.require_permission("audit.view")
    stmt = select(AuditLog).where(AuditLog.org_id == tenant.org_id)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if resource_type:
        stmt = stmt.where(AuditLog.resource_type == resource_type)
    stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit)
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": str(a.id),
            "actor_user_id": str(a.actor_user_id) if a.actor_user_id else None,
            "action": a.action,
            "resource_type": a.resource_type,
            "resource_id": str(a.resource_id) if a.resource_id else None,
            "details": a.details,
            "created_at": a.created_at,
        }
        for a in rows
    ]


async def _role_permissions(db: AsyncSession, role_id: uuid.UUID):
    rows = (
        await db.execute(
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
        )
    ).scalars().all()
    return sorted(rows)