"""
Tenancy — TenantContext, org-scoped access, permission checks, and audit logging.
Organization == Tenant. All Phase 1 services are tenant-scoped via this module.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Set
import uuid

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user_db, get_db_session
from models.core import User, Role, Organization
from models.tenancy import AuditLog, Permission, RolePermission


@dataclass
class TenantContext:
    user: User
    organization: Optional[Organization]
    roles: List[Role] = field(default_factory=list)
    permissions: Set[str] = field(default_factory=set)
    org_id: Optional[uuid.UUID] = None

    def require_permission(self, code: str) -> None:
        if code not in self.permissions and "platform.admin" not in self.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {code}",
            )

    def require_org(self) -> uuid.UUID:
        if not self.org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with an organization",
            )
        return self.org_id


async def load_user_permissions(db: AsyncSession, role_id: Optional[uuid.UUID]) -> Set[str]:
    if not role_id:
        return set()
    stmt = (
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(RolePermission.role_id == role_id)
    )
    result = await db.execute(stmt)
    return set(result.scalars().all())


async def get_tenant_context(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user_db),
) -> TenantContext:
    """Resolve the tenant context for the current request."""
    org = None
    if user.org_id:
        org = await db.get(Organization, user.org_id)
        if org and not org.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization is inactive",
            )

    roles = []
    if user.role_id:
        role = await db.get(Role, user.role_id)
        if role:
            roles.append(role)

    permissions = await load_user_permissions(db, user.role_id)

    return TenantContext(
        user=user,
        organization=org,
        roles=roles,
        permissions=permissions,
        org_id=org.id if org else None,
    )


async def require_permission(code: str):
    async def _dep(
        tenant: TenantContext = Depends(get_tenant_context),
    ) -> TenantContext:
        tenant.require_permission(code)
        return tenant

    return _dep


async def write_audit_log(
    db: AsyncSession,
    tenant: TenantContext,
    action: str,
    resource_type: str,
    resource_id: Optional[uuid.UUID] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Persist an audit entry within the caller's transaction."""
    entry = AuditLog(
        org_id=tenant.org_id,
        actor_user_id=tenant.user.id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(entry)
    return entry