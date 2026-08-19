import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from models.core import Role
from models.tenancy import AuditLog, Permission, RolePermission
from services.tenancy import TenantContext, write_audit_log


async def test_tenant_context_has_permissions(tenant):
    assert tenant.org_id is not None
    assert "platform.admin" in tenant.permissions
    assert "audit.view" in tenant.permissions


async def test_require_permission_ok(tenant):
    tenant.require_permission("rbac.manage")


async def test_require_permission_denied():
    t = TenantContext(user=type("U", (), {"id": uuid.uuid4()})(), organization=None, permissions=set())
    with pytest.raises(HTTPException) as exc:
        t.require_permission("rbac.manage")
    assert exc.value.status_code == 403


async def test_require_org_enforced():
    t = TenantContext(user=type("U", (), {"id": uuid.uuid4()})(), organization=None, org_id=None)
    with pytest.raises(HTTPException) as exc:
        t.require_org()
    assert exc.value.status_code == 403


async def test_audit_log_written(session, tenant):
    await write_audit_log(
        session,
        tenant,
        action="test.action",
        resource_type="test",
        resource_id=uuid.uuid4(),
        details={"key": "value"},
    )
    await session.commit()
    rows = (await session.execute(select(AuditLog))).scalars().all()
    assert len(rows) == 1
    assert rows[0].org_id == tenant.org_id
    assert rows[0].details == {"key": "value"}


async def test_grant_permission_to_role(session, tenant):
    new_perm = Permission(code="mission.delete", name="Delete missions")
    session.add(new_perm)
    await session.commit()
    await session.refresh(new_perm)

    session.add(RolePermission(role_id=tenant.roles[0].id, permission_id=new_perm.id))
    await session.commit()

    codes = (
        await session.execute(
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == tenant.roles[0].id)
        )
    ).scalars().all()
    assert "mission.delete" in codes