"""
Transactional Outbox — durable domain events emitted in the same transaction
as the business change that produced them. See docs/DATA_MODEL_MIGRATION_PLAN.md.

Consumers (e.g. Celery workers / webhooks / edge orchestrator) poll PENDING
events via publish_pending. Publishing is idempotent.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.events import OutboxEvent

logger = logging.getLogger(__name__)

PUBLISH_HOOKS = {}


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
    """Dispatch up to `limit` pending events. Returns count successfully published."""
    stmt = (
        select(OutboxEvent)
        .where(OutboxEvent.status == "PENDING")
        .order_by(OutboxEvent.created_at)
        .limit(limit)
    )
    result = await db.execute(stmt)
    events = result.scalars().all()

    published = 0
    for event in events:
        hook = _match_hook(event.event_type)
        try:
            if hook is not None:
                ok = hook(event)
            else:
                ok = True  # no consumer registered; treat as deliverable
            if ok:
                event.status = "PUBLISHED"
                event.published_at = datetime.now(timezone.utc)
                published += 1
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to publish outbox event %s", event.id)
            event.status = "FAILED"

    if published or any(e.status == "FAILED" for e in events):
        await db.commit()
    return published


def _match_hook(event_type: str):
    for prefix, hook in PUBLISH_HOOKS.items():
        if event_type.startswith(prefix):
            return hook
    return None