import uuid
import pytest
from fastapi import HTTPException
from sqlalchemy import select

from services.orchestrator import ObservationOrchestrator
from services.readiness import StationReadinessService, ReadinessRequired
from models.station_twin import StationOperationProfile
from models.contact import ObservationJob, StationReadinessEvent

async def test_readiness_gate_blocks_execution(session, tenant, scheduled_contact):
    # 1. Setup profile (MANUAL_CONFIRMED by default)
    profile = StationOperationProfile(
        station_id=scheduled_contact["contact"].station_id,
        mission_profile_id=scheduled_contact["mission_setup"]["profile"].id,
        name="Test HDR Profile",
        operation_mode="MANUAL_CONFIRMED"
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)

    # 2. Create Job
    orch = ObservationOrchestrator(session, tenant)
    job = await orch.create_job(
        scheduled_contact["contact"].id,
        scheduled_contact["mission_setup"]["profile"].id,
        station_operation_profile_id=profile.id
    )

    # Move to PREPARING
    for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED", "DISPATCHED", "ACKNOWLEDGED", "PREPARING"):
        job = await orch.transition(job.id, state, actor="test")

    assert job.status == "PREPARING"

    # 3. Attempt execution (should fail)
    with pytest.raises(ReadinessRequired):
        await orch.execute(job.id, actor="system")

    # 4. Post Readiness (READY)
    readiness_service = StationReadinessService(session, tenant)
    await readiness_service.record_readiness(
        job_id=job.id,
        status="READY",
        checklist_results={"mcs_profile_loaded": True}
    )

    # 5. Attempt execution (should succeed)
    job = await orch.execute(job.id, actor="system")
    assert job.status == "EXECUTING"

async def test_automatic_profile_bypasses_readiness(session, tenant, scheduled_contact):
    # Setup profile AUTOMATIC
    profile = StationOperationProfile(
        station_id=scheduled_contact["contact"].station_id,
        mission_profile_id=scheduled_contact["mission_setup"]["profile"].id,
        name="Test Auto Profile",
        operation_mode="AUTOMATIC"
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)

    orch = ObservationOrchestrator(session, tenant)
    job = await orch.create_job(
        scheduled_contact["contact"].id,
        scheduled_contact["mission_setup"]["profile"].id,
        station_operation_profile_id=profile.id
    )

    for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED", "DISPATCHED", "ACKNOWLEDGED", "PREPARING"):
        job = await orch.transition(job.id, state, actor="test")

    # Attempt execution (should succeed without readiness event)
    job = await orch.execute(job.id, actor="system")
    assert job.status == "EXECUTING"
