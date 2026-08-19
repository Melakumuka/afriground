"""
Phase 3.1/4.1 tests — API key lifecycle (hash storage, verify, revoke) and
Redis rate-limit tier enforcement.
"""
import uuid

import pytest
from sqlalchemy import select

from models.data import APIKey
from services import api_keys


async def test_generate_returns_plaintext_and_stores_hash(session, tenant):
    row, plaintext = api_keys.generate_api_key(
        session, tenant.org_id, name="ops-bot", scopes=["jobs:read"], tier="standard"
    )
    await session.commit()

    assert plaintext.startswith("agk_")
    assert len(plaintext) > len("agk_")
    assert row.key_hash != plaintext
    assert row.is_active is True

    stored = await session.get(APIKey, row.id)
    assert stored.key_hash == api_keys._hash_key(plaintext)
    assert stored.scopes == ["jobs:read"]


async def test_verify_resolves_active_key_only(session, tenant):
    row, plaintext = api_keys.generate_api_key(session, tenant.org_id, name="a")
    await session.commit()

    found = await api_keys.verify_api_key(session, plaintext)
    assert found is not None
    assert found.id == row.id

    assert await api_keys.verify_api_key(session, "agk_" + "0" * 48) is None
    assert await api_keys.verify_api_key(session, "not-a-key") is None


async def test_revoke_invalidates_key(session, tenant):
    row, plaintext = api_keys.generate_api_key(session, tenant.org_id, name="a")
    await session.commit()

    assert await api_keys.revoke_api_key(session, row.id, tenant.org_id) is True
    await session.commit()

    assert await api_keys.verify_api_key(session, plaintext) is None
    # Foreign org cannot revoke
    other = uuid.uuid4()
    assert await api_keys.revoke_api_key(session, row.id, other) is False


async def test_list_keys_scoped_to_org(session, tenant):
    api_keys.generate_api_key(session, tenant.org_id, name="one")
    from models.core import Organization

    other = Organization(name="Other Org", slug=f"other-{uuid.uuid4().hex[:8]}", is_active=True)
    session.add(other)
    await session.flush()
    api_keys.generate_api_key(session, other.id, name="foreign")
    await session.commit()

    rows = await api_keys.list_api_keys(session, tenant.org_id)
    assert len(rows) == 1
    assert rows[0].name == "one"


# ── Phase 4.1 rate limiting ──────────────────────────────────────────────────

async def test_check_rate_limit_tier_enforced(session, tenant, monkeypatch):
    import services.rate_limit as rl

    monkeypatch.setattr(rl, "TIER_LIMITS_PER_MINUTE", {"standard": 3, "pro": 10, "enterprise": 100})

    row, plaintext = api_keys.generate_api_key(session, tenant.org_id, name="rl", tier="standard")
    await session.commit()

    results = [await rl.check_rate_limit(row.id, "standard") for _ in range(4)]
    assert [r["allowed"] for r in results] == [True, True, True, False]
    assert results[3]["remaining"] == 0
    assert results[3]["reset_after_s"] > 0

    await rl.close()


async def test_check_rate_limit_fails_open_without_redis(session, tenant, monkeypatch):
    import services.rate_limit as rl

    def _boom(*args, **kwargs):
        raise ConnectionError("redis down")

    monkeypatch.setattr(rl, "_client", _boom)
    monkeypatch.setattr(rl, "TIER_LIMITS_PER_MINUTE", {"standard": 3, "pro": 10, "enterprise": 100})
    row, _ = api_keys.generate_api_key(session, tenant.org_id, name="rl2", tier="pro")
    await session.commit()

    result = await rl.check_rate_limit(row.id, "pro")
    assert result["allowed"] is True
    assert result["limit"] == 10