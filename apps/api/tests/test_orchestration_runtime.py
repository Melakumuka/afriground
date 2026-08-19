"""
Phase 2.0 orchestration runtime tests: outbox retry/backoff, simulated job
lifecycle driving, and runtime metrics.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

import services.hooks  # noqa: F401  (registers hooks)
from models.events import JobEvent, OutboxEvent
from services.orchestration_runtime import (
    SIMULATED_CHAIN,
    SystemJobDriver,
    metrics,
    process_observation_events,
)
from services.outbox import PUBLISH_HOOKS, backoff_seconds, emit, publish_pending


async def _emit(session, event_type="TEST.EVENT", aggregate_type="test"):
    event = emit(
        session,
        aggregate_type=aggregate_type,
        aggregate_id=uuid.uuid4(),
        event_type=event_type,
    )
    await session.commit()
    await session.refresh(event)
    return event


def test_backoff_seconds_exponential_with_cap(monkeypatch):
    monkeypatch.setattr("services.outbox.RETRY_BASE_S", 5.0)
    monkeypatch.setattr("services.outbox.RETRY_MAX_S", 60.0)
    assert backoff_seconds(1) == 5.0
    assert backoff_seconds(2) == 10.0
    assert backoff_seconds(3) == 20.0
    assert backoff_seconds(5) == 60.0  # capped


async def test_failed_delivery_schedules_backoff(session, monkeypatch):
    monkeypatch.setattr("services.outbox.RETRY_BASE_S", 1.0)

    @register_hook_raising("FLAPPY.")
    def flappy_hook(event):
        raise RuntimeError("down")

    event = await _emit(session, event_type="FLAPPY.BOUNCE")
    assert await publish_pending(session) == 0

    await session.refresh(event)
    assert event.status == "FAILED"
    assert event.attempt_count == 1
    assert event.next_retry_at is not None
    assert event.next_retry_at > datetime.now(timezone.utc)


async def test_failed_event_not_retried_before_backoff_elapses(session):
    @register_hook_raising("FLAPPY.")
    def flappy_hook(event):
        raise RuntimeError("still down")

    event = await _emit(session, event_type="FLAPPY.BOUNCE")
    assert await publish_pending(session) == 0
    await session.refresh(event)
    assert event.attempt_count == 1

    assert await publish_pending(session) == 0
    await session.refresh(event)
    assert event.attempt_count == 1  # no retry while backoff pending


async def test_failed_event_retried_after_backoff_elapses(session):
    @register_hook_raising("FLAPPY.")
    def flappy_hook(event):
        raise RuntimeError("down")

    event = await _emit(session, event_type="FLAPPY.BOUNCE")
    assert await publish_pending(session) == 0

    event.next_retry_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await session.commit()

    assert await publish_pending(session) == 0
    await session.refresh(event)
    assert event.attempt_count == 2
    assert event.status == "FAILED"


async def test_recovered_hook_publishes_after_retry(session):
    """A hook that stops failing lets the retried event publish."""
    calls = {"n": 0}

    @register_hook_raising("RECOVER.")
    def recover_hook(event):
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("flaky")
        return True

    event = await _emit(session, event_type="RECOVER.ME")
    assert await publish_pending(session) == 0
    event.next_retry_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    await session.commit()

    assert await publish_pending(session) == 1
    await session.refresh(event)
    assert event.status == "PUBLISHED"
    assert event.attempt_count == 1


def _register_hook(prefix, fn):
    PUBLISH_HOOKS[prefix] = fn
    return fn


def register_hook_raising(prefix):
    def wrapper(fn):
        return _register_hook(prefix, fn)
    return wrapper


# ── Simulated lifecycle driving ──────────────────────────────────────────────

async def test_simulate_drives_job_to_completion(session, tenant, scheduled_contact):
    from services.orchestrator import ObservationOrchestrator

    orch = ObservationOrchestrator(session, tenant)
    job = await orch.create_job(
        scheduled_contact["contact"].id,
        scheduled_contact["mission_setup"]["profile"].id,
    )
    for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED"):
        job = await orch.transition(job.id, state, actor="test-user")

    assert job.status == "QUEUED"

    # Drive the execution phase through the runtime (publish -> process loop).
    steps = 0
    while job.status != "COMPLETED" and steps < 20:
        await publish_pending(session, limit=50)
        await process_observation_events(session, simulate=True)
        await session.refresh(job)
        steps += 1

    assert job.status == "COMPLETED"
    assert job.completed_at is not None
    assert steps < 10  # chain has 7 steps: QUEUED..COMPLETED

    events = (
        await session.execute(
            select(JobEvent).where(JobEvent.observation_job_id == job.id).order_by(JobEvent.created_at)
        )
    ).scalars().all()
    states = [e.to_state for e in events]
    for state in SIMULATED_CHAIN:
        assert state in states


async def test_simulate_off_does_not_drive_jobs(session, tenant, scheduled_contact):
    from services.orchestrator import ObservationOrchestrator

    orch = ObservationOrchestrator(session, tenant)
    job = await orch.create_job(
        scheduled_contact["contact"].id,
        scheduled_contact["mission_setup"]["profile"].id,
    )
    for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED"):
        job = await orch.transition(job.id, state, actor="test-user")

    await publish_pending(session, limit=50)
    applied = await process_observation_events(session, simulate=False)
    assert applied == 0
    await session.refresh(job)
    assert job.status == "QUEUED"


async def test_process_events_is_idempotent(session, tenant, scheduled_contact):
    from services.orchestrator import ObservationOrchestrator

    orch = ObservationOrchestrator(session, tenant)
    job = await orch.create_job(
        scheduled_contact["contact"].id,
        scheduled_contact["mission_setup"]["profile"].id,
    )
    for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED"):
        job = await orch.transition(job.id, state, actor="test-user")

    await publish_pending(session, limit=50)
    assert await process_observation_events(session, simulate=True) == 1
    await session.refresh(job)
    assert job.status == "DISPATCHED"

    # Re-running without new events must not advance again.
    assert await process_observation_events(session, simulate=True) == 0
    await session.refresh(job)
    assert job.status == "DISPATCHED"


async def test_system_driver_records_events_and_emits(session, tenant, scheduled_contact):
    from services.orchestrator import ObservationOrchestrator

    orch = ObservationOrchestrator(session, tenant)
    job = await orch.create_job(
        scheduled_contact["contact"].id,
        scheduled_contact["mission_setup"]["profile"].id,
    )
    for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED"):
        job = await orch.transition(job.id, state, actor="test-user")

    driver = SystemJobDriver(session)
    advanced = await driver.advance(job.id, "DISPATCHED", reason="edge ready")
    assert advanced.status == "DISPATCHED"
    await session.commit()

    job_events = (
        await session.execute(
            select(JobEvent).where(
                JobEvent.observation_job_id == job.id,
                JobEvent.to_state == "DISPATCHED",
                JobEvent.actor == "system:orchestrator",
            )
        )
    ).scalars().all()
    assert job_events


# ── Metrics ──────────────────────────────────────────────────────────────────

async def test_metrics_reflect_outbox_state(session):
    def hold_hook(event):
        return False  # keeps the event PENDING

    _register_hook("HOLD.", hold_hook)

    await _emit(session, event_type="HOLD.ME")             # stays PENDING
    published_event = await _emit(session, event_type="MISC.A")
    await publish_pending(session)

    m = await metrics(session)
    outbox = m["outbox"]
    assert outbox["by_status"]["PENDING"] == 1
    assert outbox["by_status"]["PUBLISHED"] == 1
    assert outbox["total"] == 2
    assert outbox["oldest_pending_at"] is not None
    assert outbox["oldest_pending_age_s"] >= 0
    assert outbox["backpressure"] == 1
    assert "jobs_by_status" in m

    PUBLISH_HOOKS.pop("HOLD.", None)