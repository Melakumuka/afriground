"""
Phase 2.1/2.2 tests — edge agent heartbeat/time ingestion, telemetry,
missed-heartbeat watchdog, and station quality recompute.
"""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from models.station import Incident
from models.station_twin import (
    StationAgentIdentity,
    StationHeartbeat,
    StationQualityScore,
    StationTelemetryReading,
    StationTimeStatus,
)
from models.events import OutboxEvent
from services.edge_agent import EdgeAgentService, check_missed_heartbeats


async def test_register_agent_and_heartbeat(session, tenant, mission_setup):
    svc = EdgeAgentService(session, tenant)
    agent = await svc.register_agent(mission_setup["station"].id, "ag-1", agent_version="1.0.0")
    assert agent.status == "active"

    hb = await svc.report_heartbeat(mission_setup["station"].id, "ag-1", "1.0.0", {"cpu_pct": 20})
    assert hb.received_at is not None

    rows = (
        await session.execute(
            select(StationHeartbeat).where(StationHeartbeat.agent_id == "ag-1")
        )
    ).scalars().all()
    assert len(rows) == 1

    events = (
        await session.execute(
            select(OutboxEvent).where(OutboxEvent.event_type == "AGENT.HEARTBEAT")
        )
    ).scalars().all()
    assert len(events) == 1
    assert events[0].status == "PENDING"


async def test_time_status_large_offset_degrades_station(session, tenant, mission_setup):
    svc = EdgeAgentService(session, tenant)
    await svc.register_agent(mission_setup["station"].id, "ag-2")
    row = await svc.report_time_status(
        mission_setup["station"].id, "ag-2",
        sync_status="UNSYNCED", offset_ms=250.0, clock_source="ntp",
    )
    assert row.sync_status == "UNSYNCED"

    await session.refresh(mission_setup["station"])
    assert mission_setup["station"].status == "degraded"


async def test_telemetry_power_failure_opens_incident(session, tenant, mission_setup):
    svc = EdgeAgentService(session, tenant)
    await svc.register_agent(mission_setup["station"].id, "ag-3")

    reading = await svc.ingest_telemetry(
        mission_setup["station"].id, "ag-3", "power", {"main": False, "battery_pct": 5}
    )
    assert reading.telemetry_type == "power"

    incidents = (
        await session.execute(
            select(Incident).where(Incident.station_id == mission_setup["station"].id)
        )
    ).scalars().all()
    assert len(incidents) == 1
    assert incidents[0].severity == "high"
    assert incidents[0].status == "open"

    # Idempotent: no duplicate incidents.
    await svc.ingest_telemetry(mission_setup["station"].id, "ag-3", "power", {"main": False})
    incidents = (
        await session.execute(
            select(Incident).where(Incident.station_id == mission_setup["station"].id)
        )
    ).scalars().all()
    assert len(incidents) == 1


async def test_signal_telemetry_does_not_open_incident(session, tenant, mission_setup):
    svc = EdgeAgentService(session, tenant)
    await svc.register_agent(mission_setup["station"].id, "ag-4")
    await svc.ingest_telemetry(mission_setup["station"].id, "ag-4", "signal", {"snr_db": 18.5})
    incidents = (
        await session.execute(
            select(Incident).where(Incident.station_id == mission_setup["station"].id)
        )
    ).scalars().all()
    assert incidents == []


async def test_watchdog_flags_missed_heartbeat(session, tenant, mission_setup):
    svc = EdgeAgentService(session, tenant)
    await svc.register_agent(mission_setup["station"].id, "ag-5")
    agent = (
        await session.execute(
            select(StationAgentIdentity).where(StationAgentIdentity.agent_id == "ag-5")
        )
    ).scalars().first()
    agent.last_heartbeat_at = datetime.now(timezone.utc) - timedelta(minutes=10)
    await session.commit()

    flagged = await check_missed_heartbeats(session, threshold_s=60)
    assert flagged == 1

    await session.refresh(mission_setup["station"])
    assert mission_setup["station"].status == "degraded"

    incidents = (
        await session.execute(
            select(Incident).where(Incident.station_id == mission_setup["station"].id)
        )
    ).scalars().all()
    assert len(incidents) == 1


async def test_recompute_quality(session, tenant, mission_setup):
    svc = EdgeAgentService(session, tenant)
    await svc.register_agent(mission_setup["station"].id, "ag-6")
    for snr in (15.0, 20.0, 22.0):
        await svc.ingest_telemetry(mission_setup["station"].id, "ag-6", "signal", {"snr_db": snr})
    await svc.report_time_status(mission_setup["station"].id, "ag-6", "SYNCED", 2.0, "ntp")

    q = await svc.recompute_quality(mission_setup["station"].id)
    assert q.score > 0
    assert q.availability == 100.0  # operational station with fresh heartbeats

    latest = await svc.latest_quality(mission_setup["station"].id)
    assert latest.id == q.id

    # Time-status + quality rows recorded.
    times = (
        await session.execute(select(StationTimeStatus).where(StationTimeStatus.station_id == mission_setup["station"].id))
    ).scalars().all()
    assert times
    scores = (
        await session.execute(select(StationQualityScore).where(StationQualityScore.station_id == mission_setup["station"].id))
    ).scalars().all()
    assert len(scores) == 1