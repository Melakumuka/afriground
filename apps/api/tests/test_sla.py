"""
Phase 3.0 tests — SLA enforcement on job completion, contract usage.
"""
from datetime import timedelta

from sqlalchemy import select

from models.events import OutboxEvent
from models.mission import MissionSLA, SLASLAViolation
from services.commercial_engine import CommercialEngine
from services.orchestrator import ObservationOrchestrator
from services.sla import SLAService

JOB_CHAIN = (
    "REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED",
    "DISPATCHED", "ACKNOWLEDGED", "PREPARING", "EXECUTING",
    "RECEIVING", "PROCESSING", "COMPLETED",
)


async def _add_sla(session, mission_id, sla_type, target, unit="seconds"):
    sla = MissionSLA(
        mission_id=mission_id,
        sla_type=sla_type,
        target_value=target,
        unit=unit,
    )
    session.add(sla)
    await session.flush()


async def _make_job(session, tenant, scheduled_contact, final="COMPLETED"):
    orch = ObservationOrchestrator(session, tenant)
    job = await orch.create_job(
        scheduled_contact["contact"].id,
        scheduled_contact["mission_setup"]["profile"].id,
    )
    stop_at = "QUEUED" if final in ("FAILED", "QUEUED") else None
    for state in JOB_CHAIN:
        job = await orch.transition(job.id, state, actor="test-user")
        if state == stop_at:
            break
    if final == "FAILED":
        job = await orch.transition(job.id, "FAILED", actor="test-user")
    return job


async def _slow_job(session, tenant, scheduled_contact, delay_seconds=600):
    """A COMPLETED job whose wall-clock processing time exceeds the delay."""
    from datetime import timedelta

    job = await _make_job(session, tenant, scheduled_contact)
    job.completed_at = job.created_at + timedelta(seconds=delay_seconds)
    await session.flush()
    return job


async def test_timeliness_breach_recorded_and_emitted(session, tenant, scheduled_contact):
    mission = scheduled_contact["mission_setup"]["mission"]
    await _add_sla(session, mission.id, "timeliness", 1.0, unit="seconds")

    job = await _slow_job(session, tenant, scheduled_contact)
    assert job.status == "COMPLETED"

    violations = await SLAService(session).enforce_job(job)
    assert len(violations) == 1
    v = violations[0]
    assert v.sla_type == "timeliness"
    assert v.actual_value > v.target_value
    assert v.status == "open"

    events = (
        await session.execute(
            select(OutboxEvent).where(OutboxEvent.event_type == "SLA.VIOLATION")
        )
    ).scalars().all()
    assert len(events) == 1
    assert events[0].payload["job_id"] == str(job.id)

    # Idempotent: enforcing again must not duplicate the breach.
    again = await SLAService(session).enforce_job(job)
    assert len(again) == 0
    count = (
        await session.execute(select(SLASLAViolation))
    ).scalars().all()
    assert len(count) == 1


async def test_success_rate_sla_no_violation_on_success(session, tenant, scheduled_contact):
    mission = scheduled_contact["mission_setup"]["mission"]
    await _add_sla(session, mission.id, "success_rate", 50.0, unit="percent")

    job = await _make_job(session, tenant, scheduled_contact)
    violations = await SLAService(session).enforce_job(job)
    assert violations == []


async def test_success_rate_violation_on_failure(session, tenant, scheduled_contact):
    mission = scheduled_contact["mission_setup"]["mission"]
    await _add_sla(session, mission.id, "success_rate", 100.0, unit="percent")

    job = await _make_job(session, tenant, scheduled_contact, final="FAILED")
    violations = await SLAService(session).enforce_job(job)
    assert len(violations) == 1
    assert violations[0].sla_type == "success_rate"
    assert violations[0].actual_value == 0.0


async def test_runtime_enforces_sla_on_terminal_transition(session, tenant, scheduled_contact):
    """SystemJobDriver terminal transitions trigger enforcement automatically."""
    from datetime import timedelta
    from services.orchestration_runtime import process_observation_events
    from services.outbox import publish_pending

    mission = scheduled_contact["mission_setup"]["mission"]
    await _add_sla(session, mission.id, "timeliness", 1.0, unit="seconds")

    job = await _make_job(session, tenant, scheduled_contact, final="QUEUED")
    job.created_at = job.created_at - timedelta(seconds=600)
    await session.flush()

    steps = 0
    while job.status != "COMPLETED" and steps < 20:
        await publish_pending(session, limit=50)
        await process_observation_events(session, simulate=True)
        await session.refresh(job)
        steps += 1

    assert job.status == "COMPLETED"

    count = (
        await session.execute(select(SLASLAViolation))
    ).scalars().all()
    assert len(count) == 1


async def test_contract_usage_aggregates_completed_jobs(session, tenant, scheduled_contact):
    from models.core import Contract

    contact = scheduled_contact["contact"]
    expected_minutes = max(
        int((contact.scheduled_end - contact.scheduled_start).total_seconds() // 60), 0
    )

    contract = Contract(
        org_id=tenant.org_id,
        start_date=contact.scheduled_start - timedelta(days=1),
        end_date=contact.scheduled_end + timedelta(days=1),
        reserved_capacity_minutes=1000,
        sla_availability_target=99.5,
        status="active",
    )
    session.add(contract)
    await session.commit()

    await _make_job(session, tenant, scheduled_contact)

    engine = CommercialEngine(session)
    usage = await engine.get_contract_usage(contract.id)
    assert usage.used_minutes == expected_minutes
    assert usage.remaining_minutes == 1000 - expected_minutes