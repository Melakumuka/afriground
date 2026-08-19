import os
import uuid
from datetime import datetime, timezone

import pytest

import services.hooks  # noqa: F401  (registers hooks)
from models.events import OutboxEvent
from services.outbox import emit, publish_pending, register_publish_hook, PUBLISH_HOOKS


async def _emit_event(session, event_type="TEST.EVENT", aggregate_type="test"):
    aggregate_id = uuid.uuid4()
    event = emit(session, aggregate_type=aggregate_type, aggregate_id=aggregate_id, event_type=event_type)
    await session.commit()
    await session.refresh(event)
    return event


async def test_emit_writes_pending_outbox_row(session):
    event = await _emit_event(session)
    assert event.status == "PENDING"
    assert event.published_at is None


async def test_publish_pending_without_hook_marks_published(session):
    event = await _emit_event(session, event_type="UNKNOWN.EVENT")
    published = await publish_pending(session)
    assert published == 1

    await session.refresh(event)
    assert event.status == "PUBLISHED"
    assert event.published_at is not None


async def test_publish_pending_only_publishes_once(session):
    event = await _emit_event(session, event_type="UNKNOWN.EVENT")
    assert await publish_pending(session) == 1
    assert await publish_pending(session) == 0
    await session.refresh(event)
    assert event.status == "PUBLISHED"


async def test_hook_failure_marks_failed(session):
    captured = {}

    @register_publish_hook("FLAPPY.")
    def flappy_hook(event):
        captured["event_type"] = event.event_type
        raise RuntimeError("webhook unreachable")

    event = await _emit_event(session, event_type="FLAPPY.BOUNCE")
    assert await publish_pending(session) == 0
    await session.refresh(event)
    assert event.status == "FAILED"
    assert captured["event_type"] == "FLAPPY.BOUNCE"

    PUBLISH_HOOKS.pop("FLAPPY.", None)


async def test_hook_false_skips_and_retries(session):
    """A hook returning False leaves the event PENDING for a later retry."""

    @register_publish_hook("TARDY.")
    def tardy_hook(event):
        return False

    event = await _emit_event(session, event_type="TARDY.EVENT")
    assert await publish_pending(session) == 0
    await session.refresh(event)
    assert event.status == "PENDING"

    PUBLISH_HOOKS.pop("TARDY.", None)


async def test_webhook_hook_no_url_is_ok(session, monkeypatch):
    monkeypatch.setattr(services.hooks, "WEBHOOK_URL", None)
    event = await _emit_event(session, event_type="OBSERVATION_JOB.SCHEDULED")
    assert await publish_pending(session) == 1
    await session.refresh(event)
    assert event.status == "PUBLISHED"


async def test_worker_drain_function(engine, session):
    """The worker's core drain loop must be idempotent and safe."""
    from sqlalchemy.ext.asyncio import async_sessionmaker
    from scripts.outbox_worker import drain_once

    event = await _emit_event(session, event_type="STATION.REGISTERED")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    published = await drain_once(factory, limit=10)
    assert published == 1

    await session.refresh(event)
    assert event.status == "PUBLISHED"
    # second drain is a no-op
    assert await drain_once(factory, limit=10) == 0