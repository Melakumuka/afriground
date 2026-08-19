"""
Rate Limiting (Phase 4.1) — Redis-backed sliding-window token bucket for API
key tiers. Runs inline with API-key auth; Redis failures fail open with a
warning so a cache outage never takes down the data plane.
"""
import asyncio
import logging
import time
import uuid

from config import settings

logger = logging.getLogger(__name__)

# Requests per minute per tier (Phase 4.1).
TIER_LIMITS_PER_MINUTE = {
    "standard": 60,
    "pro": 600,
    "enterprise": 6000,
}

DEFAULT_LIMIT = TIER_LIMITS_PER_MINUTE["standard"]

# Redis clients keyed by event loop id — asyncio clients are loop-bound, and
# tests exercise the limiter from multiple loops (pytest vs TestClient portal).
_clients = {}


def _client():
    loop = asyncio.get_running_loop()
    key = id(loop)
    client = _clients.get(key)
    if client is None:
        import redis.asyncio as aioredis

        client = aioredis.from_url(
            settings.redis_url, socket_connect_timeout=1, socket_timeout=1, decode_responses=True
        )
        _clients[key] = client
    return client


async def check_rate_limit(key_id: uuid.UUID, tier: str) -> dict:
    """Record one request for the key and report {allowed, remaining, limit,
    reset_after_s}. Raises nothing — the caller decides on 429."""
    limit = TIER_LIMITS_PER_MINUTE.get(tier, DEFAULT_LIMIT)
    window = int(time.time() // 60)
    bucket = f"rl:key:{key_id}:{window}"

    try:
        client = _client()
        count = await client.incr(bucket)
        if count == 1:
            await client.expire(bucket, 120)
        remaining = max(limit - count, 0)
        return {"allowed": count <= limit, "remaining": remaining, "limit": limit,
                "reset_after_s": 60 - int(time.time() % 60)}
    except Exception:  # noqa: BLE001 — fail open on Redis outage
        logger.warning("rate limiter unavailable for key %s: fail-open", key_id)
        return {"allowed": True, "remaining": limit, "limit": limit, "reset_after_s": 0}


async def close() -> None:
    for client in _clients.values():
        try:
            await client.aclose()
        except Exception:  # noqa: BLE001
            logger.warning("rate limiter shutdown failed for a loop client", exc_info=True)
    _clients.clear()