"""
Route-level integration tests: real FastAPI app, real test DB, mocked Supabase
auth (dependency overrides on get_db_session / get_current_user_db).
"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import main
from auth import get_db_session
from services.tenancy import get_tenant_context

from conftest import TEST_URL, _seed_tenancy, PERMISSION_CODES


@pytest.fixture
def client():
    """TestClient with its own engine; connections are created inside the
    portal loop (NullPool), so no cross-loop sharing with pytest's loops."""
    import asyncio
    from sqlalchemy.pool import NullPool

    app = main.app
    engine = create_async_engine(TEST_URL, poolclass=NullPool, pool_pre_ping=True)
    maker = async_sessionmaker(engine, expire_on_commit=False)

    async def _override_db():
        async with maker() as s:
            yield s

    app.dependency_overrides[get_db_session] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())


@pytest.fixture
def seeded_user():
    """Seed a user + org via its own throwaway engine; returns detached data."""
    import asyncio
    from sqlalchemy.pool import NullPool

    engine = create_async_engine(TEST_URL, poolclass=NullPool, pool_pre_ping=True)
    maker = async_sessionmaker(engine, expire_on_commit=False)

    async def _seed():
        async with maker() as s:
            from conftest import _truncate_all

            await _truncate_all(s)
            return await _seed_tenancy(s, PERMISSION_CODES)

    try:
        data = asyncio.run(_seed())
    finally:
        asyncio.run(engine.dispose())
    return data


@pytest.fixture
def authed_client(client, seeded_user):
    """Override the tenant dependency to resolve to the seeded user."""
    app = main.app
    app.dependency_overrides[get_tenant_context] = _tenant_override_for(seeded_user)
    yield client
    app.dependency_overrides.pop(get_tenant_context, None)


def _tenant_override_for(seeded_user):
    async def _override_tenant():
        return seeded_user["tenant"]

    return _override_tenant


def test_health_endpoint_exists(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_me_requires_auth(client):
    resp = client.get("/api/v1/tenancy/me")
    assert resp.status_code == 401


def test_tenancy_me_returns_tenant(authed_client, seeded_user):
    resp = authed_client.get("/api/v1/tenancy/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == seeded_user["user"].email
    assert body["organization"]["id"] == str(seeded_user["org"].id)
    assert "rbac.manage" in body["permissions"]


def test_tenancy_permissions_listed(authed_client):
    resp = authed_client.get("/api/v1/tenancy/permissions")
    assert resp.status_code == 200
    codes = [p["code"] for p in resp.json()]
    assert "platform.admin" in codes


def test_tenancy_roles_listed(authed_client):
    resp = authed_client.get("/api/v1/tenancy/roles")
    assert resp.status_code == 200
    assert any(r["name"] == "Test Platform Admin" for r in resp.json())


def test_job_list_requires_permission(client, seeded_user):
    """A tenant without job.operate must get 403 on job endpoints."""
    from services.tenancy import get_tenant_context as gtc
    from services.tenancy import TenantContext

    app = main.app

    async def _override_tenant():
        return TenantContext(
            user=seeded_user["user"],
            organization=seeded_user["org"],
            roles=[],
            permissions=set(),  # no permissions at all
            org_id=seeded_user["org"].id,
        )

    app.dependency_overrides[gtc] = _override_tenant
    resp = client.post("/api/v1/contact/jobs?scheduled_contact_id=" + str(uuid.uuid4()) + "&mission_profile_id=" + str(uuid.uuid4()))
    assert resp.status_code == 403
    app.dependency_overrides.pop(gtc, None)


def test_audit_logs_requires_permission(client, seeded_user):
    from services.tenancy import get_tenant_context as gtc
    from services.tenancy import TenantContext

    app = main.app

    async def _override_tenant():
        return TenantContext(
            user=seeded_user["user"],
            organization=seeded_user["org"],
            roles=[],
            permissions=set(["audit.view"]),
            org_id=seeded_user["org"].id,
        )

    app.dependency_overrides[gtc] = _override_tenant
    resp = client.get("/api/v1/tenancy/audit-logs")
    assert resp.status_code == 200
    app.dependency_overrides.pop(gtc, None)


def test_stations_mutation_requires_station_manage(client, seeded_user):
    """POST /api/v1/stations/{id}/tx requires station.manage; a tenant without
    permissions must get 403 before touching the DB."""
    from services.tenancy import get_tenant_context as gtc
    from services.tenancy import TenantContext

    app = main.app

    async def _override_tenant():
        return TenantContext(
            user=seeded_user["user"],
            organization=seeded_user["org"],
            roles=[],
            permissions=set(),
            org_id=seeded_user["org"].id,
        )

    app.dependency_overrides[gtc] = _override_tenant
    resp = client.post(f"/api/v1/stations/{uuid.uuid4()}/tx?enabled=true")
    assert resp.status_code == 403
    app.dependency_overrides.pop(gtc, None)


def test_regulatory_register_requires_station_manage(client, seeded_user):
    from services.tenancy import get_tenant_context as gtc
    from services.tenancy import TenantContext

    app = main.app

    async def _override_tenant():
        return TenantContext(
            user=seeded_user["user"],
            organization=seeded_user["org"],
            roles=[],
            permissions=set(),
            org_id=seeded_user["org"].id,
        )

    app.dependency_overrides[gtc] = _override_tenant
    resp = client.post(
        "/api/v1/regulatory/stations/register"
        f"?code=ZA-NOPERM-01&name=No+Perm&country=ZA&latitude=0&longitude=0&altitude_m=0"
    )
    assert resp.status_code == 403
    app.dependency_overrides.pop(gtc, None)


def test_orchestration_metrics_requires_admin(client, seeded_user):
    """GET /api/v1/orchestration/metrics requires platform.admin."""
    from services.tenancy import get_tenant_context as gtc
    from services.tenancy import TenantContext

    app = main.app

    async def _override_tenant():
        return TenantContext(
            user=seeded_user["user"],
            organization=seeded_user["org"],
            roles=[],
            permissions=set(),
            org_id=seeded_user["org"].id,
        )

    app.dependency_overrides[gtc] = _override_tenant
    assert client.get("/api/v1/orchestration/metrics").status_code == 403
    app.dependency_overrides.pop(gtc, None)


def test_orchestration_metrics_ok_for_admin(authed_client):
    resp = authed_client.get("/api/v1/orchestration/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert "outbox" in body
    assert "jobs_by_status" in body


def test_edge_heartbeat_requires_station_manage(client, seeded_user):
    """POST /api/v1/edge/.../heartbeat requires station.manage."""
    from services.tenancy import get_tenant_context as gtc
    from services.tenancy import TenantContext

    app = main.app

    async def _override_tenant():
        return TenantContext(
            user=seeded_user["user"],
            organization=seeded_user["org"],
            roles=[],
            permissions=set(),
            org_id=seeded_user["org"].id,
        )

    app.dependency_overrides[gtc] = _override_tenant
    resp = client.post(
        f"/api/v1/edge/stations/{uuid.uuid4()}/agents/some-agent/heartbeat",
        json={"agent_version": "1.0.0", "metrics": {}},
    )
    assert resp.status_code == 403
    app.dependency_overrides.pop(gtc, None)


def test_edge_telemetry_list_unknown_station_404(authed_client):
    resp = authed_client.get(f"/api/v1/edge/stations/{uuid.uuid4()}/telemetry")
    assert resp.status_code == 404


def test_edge_quality_unknown_station_404(authed_client):
    resp = authed_client.get(f"/api/v1/edge/stations/{uuid.uuid4()}/quality")
    assert resp.status_code == 404


# ── Phase 3 API tests ────────────────────────────────────────────────────────

def test_api_key_create_requires_permission(client, seeded_user):
    from services.tenancy import get_tenant_context as gtc
    from services.tenancy import TenantContext

    app = main.app

    async def _override_tenant():
        return TenantContext(
            user=seeded_user["user"],
            organization=seeded_user["org"],
            roles=[],
            permissions=set(),
            org_id=seeded_user["org"].id,
        )

    app.dependency_overrides[gtc] = _override_tenant
    resp = client.post("/api/v1/keys", json={"name": "no-perm"})
    assert resp.status_code == 403
    app.dependency_overrides.pop(gtc, None)


def test_api_key_create_and_me(authed_client, seeded_user):
    resp = authed_client.post("/api/v1/keys", json={"name": "ops-bot", "scopes": ["jobs:read"]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["api_key"].startswith("agk_")
    assert body["scopes"] == ["jobs:read"]

    me = authed_client.get("/api/v1/keys/me", headers={"X-API-Key": body["api_key"]})
    assert me.status_code == 200
    me_body = me.json()
    assert me_body["org_id"] == str(seeded_user["org"].id)

    me_bad = authed_client.get("/api/v1/keys/me", headers={"X-API-Key": "agk_bad" * 6})
    assert me_bad.status_code == 401

    listed = authed_client.get("/api/v1/keys")
    assert listed.status_code == 200
    assert any(k["name"] == "ops-bot" for k in listed.json())

    revoked = authed_client.delete(f"/api/v1/keys/{body['id']}")
    assert revoked.status_code == 200

    me_revoked = authed_client.get("/api/v1/keys/me", headers={"X-API-Key": body["api_key"]})
    assert me_revoked.status_code == 401


def test_webhook_crud_and_permission(client, authed_client, seeded_user):
    from services.tenancy import get_tenant_context as gtc
    from services.tenancy import TenantContext

    app = main.app

    async def _override_tenant():
        return TenantContext(
            user=seeded_user["user"],
            organization=seeded_user["org"],
            roles=[],
            permissions=set(),
            org_id=seeded_user["org"].id,
        )

    app.dependency_overrides[gtc] = _override_tenant
    resp = client.post("/api/v1/webhooks", json={"url": "https://x.test/h", "events": ["OBSERVATION_JOB."]})
    assert resp.status_code == 403
    app.dependency_overrides.pop(gtc, None)
    app.dependency_overrides[gtc] = _tenant_override_for(seeded_user)

    created = authed_client.post(
        "/api/v1/webhooks",
        json={"url": "https://x.test/h", "events": ["OBSERVATION_JOB."]},
    )
    assert created.status_code == 200
    wh = created.json()
    assert wh["is_active"] is True

    listed = authed_client.get("/api/v1/webhooks")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    toggled = authed_client.patch(f"/api/v1/webhooks/{wh['id']}/toggle")
    assert toggled.status_code == 200
    assert toggled.json()["is_active"] is False

    deleted = authed_client.delete(f"/api/v1/webhooks/{wh['id']}")
    assert deleted.status_code == 200


def test_sla_violations_requires_admin(client, authed_client, seeded_user):
    from services.tenancy import get_tenant_context as gtc
    from services.tenancy import TenantContext

    app = main.app

    async def _override_tenant():
        return TenantContext(
            user=seeded_user["user"],
            organization=seeded_user["org"],
            roles=[],
            permissions=set(),
            org_id=seeded_user["org"].id,
        )

    app.dependency_overrides[gtc] = _override_tenant
    resp = client.get("/api/v1/business/sla-violations")
    assert resp.status_code == 403
    app.dependency_overrides.pop(gtc, None)
    app.dependency_overrides[gtc] = _tenant_override_for(seeded_user)

    ok = authed_client.get("/api/v1/business/sla-violations")
    assert ok.status_code == 200
    assert ok.json() == []


def test_network_ranking_requires_admin(client, authed_client, seeded_user):
    from services.tenancy import get_tenant_context as gtc
    from services.tenancy import TenantContext

    app = main.app

    async def _override_tenant():
        return TenantContext(
            user=seeded_user["user"],
            organization=seeded_user["org"],
            roles=[],
            permissions=set(),
            org_id=seeded_user["org"].id,
        )

    app.dependency_overrides[gtc] = _override_tenant
    resp = client.get("/api/v1/network/ranking")
    assert resp.status_code == 403
    app.dependency_overrides.pop(gtc, None)
    app.dependency_overrides[gtc] = _tenant_override_for(seeded_user)

    ok = authed_client.get("/api/v1/network/ranking")
    assert ok.status_code == 200
    assert isinstance(ok.json(), list)


def test_healthz_reports_db(authed_client):
    resp = authed_client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["db"] == "up"
