import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from models.contact import ObservationJob, ExecutionReceipt
from models.events import JobEvent, OutboxEvent
from services.orchestrator import ObservationOrchestrator


async def test_create_job(session, tenant, scheduled_contact):
    orch = ObservationOrchestrator(session, tenant)
    contact = scheduled_contact["contact"]
    job = await orch.create_job(contact.id, scheduled_contact["mission_setup"]["profile"].id)
    assert job.status == "DRAFT"
    assert job.org_id == tenant.org_id


async def test_duplicate_job_rejected(session, tenant, scheduled_contact):
    orch = ObservationOrchestrator(session, tenant)
    contact = scheduled_contact["contact"]
    await orch.create_job(contact.id, scheduled_contact["mission_setup"]["profile"].id)
    with pytest.raises(HTTPException) as exc:
        await orch.create_job(contact.id, scheduled_contact["mission_setup"]["profile"].id)
    assert exc.value.status_code == 409


async def test_job_full_lifecycle(session, tenant, scheduled_contact):
    orch = ObservationOrchestrator(session, tenant)
    contact = scheduled_contact["contact"]
    job = await orch.create_job(contact.id, scheduled_contact["mission_setup"]["profile"].id)

    await orch.request(job.id)
    await orch.validate(job.id)
    await orch.schedule(job.id)
    await orch.enqueue(job.id)
    await orch.dispatch(job.id)
    await orch.acknowledge(job.id)
    await orch.prepare(job.id)

    # Post readiness so the execute() gate passes
    from services.readiness import StationReadinessService
    await StationReadinessService(session, tenant).record_readiness(
        job_id=job.id, status="READY",
        checklist_results={"mcs_profile_loaded": True},
    )

    await orch.execute(job.id)
    await orch.receive(job.id)
    await orch.process(job.id)
    job = await orch.complete(job.id)

    assert job.status == "COMPLETED"
    assert job.completed_at is not None
    assert job.started_at is not None


async def test_invalid_transition_rejected(session, tenant, scheduled_contact):
    orch = ObservationOrchestrator(session, tenant)
    contact = scheduled_contact["contact"]
    job = await orch.create_job(contact.id, scheduled_contact["mission_setup"]["profile"].id)

    with pytest.raises(HTTPException) as exc:
        await orch.transition(job.id, "COMPLETED")  # DRAFT -> COMPLETED invalid
    assert exc.value.status_code == 400
    assert job.status == "DRAFT"


async def test_terminal_state_blocks_further_transitions(session, tenant, scheduled_contact):
    orch = ObservationOrchestrator(session, tenant)
    contact = scheduled_contact["contact"]
    job = await orch.create_job(contact.id, scheduled_contact["mission_setup"]["profile"].id)

    await orch.cancel(job.id, reason="No longer needed")
    assert job.status == "CANCELLED"
    with pytest.raises(HTTPException) as exc:
        await orch.request(job.id)
    assert exc.value.status_code == 400


async def test_record_receipt_finalizes_job(session, tenant, scheduled_contact):
    orch = ObservationOrchestrator(session, tenant)
    contact = scheduled_contact["contact"]
    job = await orch.create_job(contact.id, scheduled_contact["mission_setup"]["profile"].id)

    await orch.request(job.id)
    await orch.validate(job.id)
    await orch.schedule(job.id)
    await orch.enqueue(job.id)
    await orch.dispatch(job.id)
    await orch.acknowledge(job.id)
    await orch.prepare(job.id)

    # Post readiness so the execute() gate passes
    from services.readiness import StationReadinessService
    await StationReadinessService(session, tenant).record_readiness(
        job_id=job.id, status="READY",
        checklist_results={"mcs_profile_loaded": True},
    )

    await orch.execute(job.id)
    await orch.receive(job.id)
    await orch.process(job.id)

    receipt = await orch.record_receipt(
        job.id, "COMPLETED", received_bytes=1024.0,
        recorded_file_url="s3://demo/recording.bin",
        signal_quality={"snr_db": 18.5},
        notes="Clean pass",
    )
    assert receipt.status == "COMPLETED"
    assert receipt.received_bytes == 1024.0

    job = await orch._get_job(job.id)
    assert job.status == "COMPLETED"

    events = await orch.list_events(job.id)
    assert len(events) == 12  # CREATED + 11 transitions (REQUESTED..COMPLETED)


async def test_outbox_events_emitted(session, tenant, scheduled_contact):
    orch = ObservationOrchestrator(session, tenant)
    contact = scheduled_contact["contact"]
    job = await orch.create_job(contact.id, scheduled_contact["mission_setup"]["profile"].id)
    await orch.request(job.id)

    events = (
        await session.execute(select(OutboxEvent).where(OutboxEvent.aggregate_id == job.id))
    ).scalars().all()
    types = {e.event_type for e in events}
    assert "OBSERVATION_JOB.CREATED" in types
    assert "OBSERVATION_JOB.REQUESTED" in types


async def test_list_jobs_scoped_by_org(session, tenant):
    # No jobs exist for a fresh tenant
    orch = ObservationOrchestrator(session, tenant)
    jobs = await orch.list_jobs()
    assert jobs == []