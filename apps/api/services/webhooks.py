"""
Per-org Webhook Fan-out (Phase 3.1) — delivers published outbox events to every
active webhook registered by the event's owning organization.

The global outbox webhook (services/hooks.py) remains the authoritative
consumer; this layer is an additive, per-customer fan-out with HMAC
signatures. Idempotency is tracked in webhook_deliveries (unique per
webhook+event pair).
"""
import asyncio
import hashlib
import hmac
import json
import logging
import urllib.request
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.data import Webhook, WebhookDelivery
from models.events import OutboxEvent

logger = logging.getLogger(__name__)

TIMEOUT_S = 5.0
DELIVERY_BATCH = 100


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _json_dumps(obj) -> str:
    def _default(o):
        if hasattr(o, "isoformat"):
            return o.isoformat()
        return str(o)

    return json.dumps(obj, default=_default)


def _signature(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def _matches(event_type: str, patterns: List[str]) -> bool:
    return any(event_type.startswith(p) for p in patterns or [])


def _post(url: str, body: bytes, secret: str) -> int:
    """Synchronous POST with HMAC signature. Returns HTTP status code."""
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-AfrGround-Signature": _signature(secret, body),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return resp.status


async def _deliver_one(event: OutboxEvent, webhook: Webhook) -> Optional[int]:
    body = _json_dumps(
        {
            "event_type": event.event_type,
            "aggregate_type": event.aggregate_type,
            "aggregate_id": str(event.aggregate_id),
            "payload": event.payload or {},
        }
    ).encode("utf-8")
    try:
        status = await asyncio.to_thread(_post, webhook.url, body, webhook.secret)
        return status if 200 <= status < 300 else status
    except Exception as exc:  # noqa: BLE001
        logger.warning("org webhook delivery failed for event %s -> %s: %s", event.id, webhook.id, exc)
        return None


async def deliver_org_webhooks(db: AsyncSession, limit: int = DELIVERY_BATCH) -> dict:
    """Fan out published outbox events to per-org webhooks.

    Returns counts of deliveries made. The caller owns the transaction.
    """
    events = (
        await db.execute(
            select(OutboxEvent)
            .where(OutboxEvent.status == "PUBLISHED")
            .order_by(OutboxEvent.created_at)
            .limit(limit)
        )
    ).scalars().all()

    delivered = 0
    failed = 0
    for event in events:
        org_id = (event.payload or {}).get("org_id")
        if not org_id:
            continue

        webhooks = (
            await db.execute(
                select(Webhook).where(
                    Webhook.org_id == org_id,
                    Webhook.is_active == True,  # noqa: E712
                )
            )
        ).scalars().all()

        for webhook in webhooks:
            if not _matches(event.event_type, webhook.events or []):
                continue

            existing = (
                await db.execute(
                    select(WebhookDelivery.id).where(
                        WebhookDelivery.webhook_id == webhook.id,
                        WebhookDelivery.outbox_event_id == event.id,
                    )
                )
            ).scalar_one_or_none()
            if existing:
                continue

            status = await _deliver_one(event, webhook)
            db.add(
                WebhookDelivery(
                    webhook_id=webhook.id,
                    outbox_event_id=event.id,
                    status="delivered" if status is not None and status < 300 else "failed",
                    response_code=status,
                    delivered_at=_now(),
                )
            )
            if status is not None and status < 300:
                delivered += 1
            else:
                failed += 1

    if delivered or failed:
        await db.commit()
    return {"delivered": delivered, "failed": failed}