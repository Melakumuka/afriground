"""
Transactional Outbox — durable domain events emitted in the same transaction
as the business change that produced them. See docs/DATA_MODEL_MIGRATION_PLAN.md.

Consumers (e.g. Celery workers / webhooks / edge orchestrator) poll PENDING
events via publish_pending. Publishing is idempotent. Failed deliveries are
retried with exponential backoff (attempt_count / next_retry_at).
"""
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.events import OutboxEvent

logger = logging.getLogger(__name__)

RETRY_BASE_S = float(os.environ.get("AFRIGROUND_OUTBOX_RETRY_BASE_S", "5"))
RETRY_MAX_S = float(os.environ.get("AFRIGROUND_OUTBOX_RETRY_MAX_S", "3600"))

PUBLISH_HOOKS = {}


def backoff_seconds(attempt: int) -> float:
    """Exponential backoff capped at RETRY_MAX_S: base * 2**(attempt-1)."""
    return min(RETRY_BASE_S * (2 ** max(attempt - 1, 0)), RETRY_MAX_S)


def register_publish_hook(event_type_prefix: str):
    """Decorator: register a callable(event: OutboxEvent) -> bool for an event type prefix."""
    def wrapper(fn):
        PUBLISH_HOOKS[event_type_prefix] = fn
        return fn
    return wrapper


def emit(
    db: AsyncSession,
    aggregate_type: str,
    aggregate_id: uuid.UUID,
    event_type: str,
    payload: Optional[dict] = None,
) -> OutboxEvent:
    """Add an outbox event to the current transaction (not yet committed)."""
    event = OutboxEvent(
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        event_type=event_type,
        payload=payload or {},
        status="PENDING",
    )
    db.add(event)
    return event


async def publish_pending(db: AsyncSession, limit: int = 50) -> int:
    """Dispatch up to `limit` due events. Returns count successfully published.

    Selects events that are PENDING or FAILED with a retry due (backoff elapsed).
    Hook failures increment attempt_count and schedule the next retry.
    """
    now = datetime.now(timezone.utc)
    stmt = (
        select(OutboxEvent)
        .where(
            or_(
                OutboxEvent.status == "PENDING",
                OutboxEvent.status == "FAILED",
            )
        )
        .order_by(OutboxEvent.created_at)
        .limit(limit)
    )
    result = await db.execute(stmt)
    events = result.scalars().all()

    published = 0
    for event in events:
        if event.status == "FAILED" and event.next_retry_at and event.next_retry_at > now:
            continue  # backoff not yet elapsed
        hook = _match_hook(event.event_type)
        try:
            if hook is not None:
                ok = hook(event)
            else:
                ok = True  # no consumer registered; treat as deliverable
            if ok:
                event.status = "PUBLISHED"
                event.published_at = now
                published += 1
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to publish outbox event %s", event.id)
            event.attempt_count = (event.attempt_count or 0) + 1
            event.next_retry_at = now + timedelta(seconds=backoff_seconds(event.attempt_count))
            event.status = "FAILED"

    if published or any(e.status == "FAILED" for e in events):
        await db.commit()
    return published


def _match_hook(event_type: str):
    for prefix, hook in PUBLISH_HOOKS.items():
        if event_type.startswith(prefix):
            return hook
    return None