"""
Phase 2.3 tests — data delivery pipeline triggered on job completion.
"""
from sqlalchemy import select

from models.data import DataDeliveryDestination, DataDeliveryJob, Dataset
from models.events import OutboxEvent
from services.delivery import DeliveryService
from services.orchestrator import ObservationOrchestrator


async def _add_destinations(session, org_id, n=2):
    dests = []
    for i in range(n):
        dest = DataDeliveryDestination(
            org_id=org_id, type="webhook",
            config={"url": f"https://example.test/dest/{i}"}, is_active=True,
        )
        session.add(dest)
        await session.flush()
        dests.append(dest)
    await session.commit()
    return dests


async def _make_completed_job(session, tenant, scheduled_contact):
    orch = ObservationOrchestrator(session, tenant)
    job = await orch.create_job(
        scheduled_contact["contact"].id,
        scheduled_contact["mission_setup"]["profile"].id,
    )
    for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED",
                  "DISPATCHED", "ACKNOWLEDGED", "PREPARING", "EXECUTING",
                  "RECEIVING", "PROCESSING", "COMPLETED"):
        job = await orch.transition(job.id, state, actor="test-user")
    return job


async def test_on_job_completed_creates_delivered_jobs(session, tenant, scheduled_contact):
    dests = await _add_destinations(session, tenant.org_id)
    job = await _make_completed_job(session, tenant, scheduled_contact)
    assert job.status == "COMPLETED"

    created = await DeliveryService(session).on_job_completed(job)
    assert len(created) == len(dests)

    for d in created:
        assert d.status == "delivered"
        assert d.checksum
        assert d.retention_expires_at is not None

    dataset = (
        await session.execute(select(Dataset).where(Dataset.observation_job_id == job.id))
    ).scalars().first()
    assert dataset is not None
    assert dataset.storage_url

    events = (
        await session.execute(
            select(OutboxEvent).where(OutboxEvent.event_type == "DATA_DELIVERY.COMPLETED")
        )
    ).scalars().all()
    assert len(events) == len(dests)


async def test_on_job_completed_idempotent(session, tenant, scheduled_contact):
    await _add_destinations(session, tenant.org_id)
    job = await _make_completed_job(session, tenant, scheduled_contact)

    first = await DeliveryService(session).on_job_completed(job)
    second = await DeliveryService(session).on_job_completed(job)

    assert len(first) == 2
    assert len(second) == 2  # reused, not duplicated

    count = (
        await session.execute(select(DataDeliveryJob))
    ).scalars().all()
    assert len(count) == 2


async def test_runtime_completes_job_and_delivers(session, tenant, scheduled_contact):
    """Full loop: runtime drives QUEUED..COMPLETED and triggers delivery."""
    from services.orchestration_runtime import process_observation_events
    from services.outbox import publish_pending

    dests = await _add_destinations(session, tenant.org_id)

    orch = ObservationOrchestrator(session, tenant)
    job = await orch.create_job(
        scheduled_contact["contact"].id,
        scheduled_contact["mission_setup"]["profile"].id,
    )
    for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED"):
        job = await orch.transition(job.id, state, actor="test-user")

    steps = 0
    while job.status != "COMPLETED" and steps < 20:
        await publish_pending(session, limit=50)
        await process_observation_events(session, simulate=True)
        await session.refresh(job)
        steps += 1

    assert job.status == "COMPLETED"

    deliveries = await DeliveryService(session).list_delivery_jobs(tenant.org_id)
    assert len(deliveries) == len(dests)
    assert all(d.status == "delivered" for d in deliveries)
    assert all(d.checksum for d in deliveries)


async def test_list_delivery_jobs_scoped_to_org(session, tenant, scheduled_contact):
    await _add_destinations(session, tenant.org_id, n=1)
    job = await _make_completed_job(session, tenant, scheduled_contact)
    await DeliveryService(session).on_job_completed(job)

    await session.commit()
    rows = await DeliveryService(session).list_delivery_jobs(tenant.org_id)
    assert len(rows) == 1