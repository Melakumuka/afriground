"""
Phase 4.0 tests — mTLS edge agent bridge: identity resolution, station-scoped
dispatch, execution chain transitions, receipts, delivery trigger, and the
agent HTTP endpoints.
"""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import main
from auth import get_db_session
from conftest import TEST_URL, _seed_tenancy, PERMISSION_CODES, _truncate_all
from models.contact import ExecutionReceipt, ObservationJob
from models.data import DataDeliveryDestination
from models.events import OutboxEvent
from models.station_twin import StationAgentIdentity
from services.agent_dispatch import AgentDispatchService, ReceiptRequest
from services.edge_agent import EdgeAgentService
from services.orchestration_runtime import SystemJobDriver, dispatch_due_jobs


def _now():
    return datetime.now(timezone.utc)


async def _registered_agent(session, station_id, agent_id="ag-test-01", **kwargs):
    svc = EdgeAgentService(session)
    agent = await svc.register_agent(station_id, agent_id, agent_version="2.0.0")
    agent.certificate_serial = f"CRT-{agent_id}"
    agent.certificate_valid_until = kwargs.pop("certificate_valid_until", _now() + timedelta(days=30))
    for k, v in kwargs.items():
        setattr(agent, k, v)
    await session.commit()
    await session.refresh(agent)
    return agent


async def _dispatched_job(session, tenant, scheduled_contact, mission_setup):
    from services.orchestrator import ObservationOrchestrator

    orch = ObservationOrchestrator(session, tenant)
    job = await orch.create_job(scheduled_contact["contact"].id, mission_setup["profile"].id)
    for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED", "DISPATCHED"):
        job = await orch.transition(job.id, state, actor="test")
    return job


# ── Service level ─────────────────────────────────────────────────────────────

async def test_assigned_jobs_only_dispatched(session, tenant, scheduled_contact, mission_setup):
    agent = await _registered_agent(session, mission_setup["station"].id)
    svc = AgentDispatchService(session, agent, mission_setup["station"])

    job = await _dispatched_job(session, tenant, scheduled_contact, mission_setup)
    jobs = await svc.assigned_jobs()
    assert [j.id for j in jobs] == [job.id]

    bundle = await svc.job_bundle(jobs[0])
    assert bundle["job_id"] == str(job.id)
    assert bundle["rf"]["band"] == "UHF"
    assert bundle["mission"] == "Test Mission"
    assert bundle["scheduled_contact"]["start"]

    await svc.acknowledge(job.id)
    assert await svc.assigned_jobs() == []  # no longer DISPATCHED


async def test_ack_and_execution_chain(session, tenant, scheduled_contact, mission_setup):
    agent = await _registered_agent(session, mission_setup["station"].id)
    svc = AgentDispatchService(session, agent, mission_setup["station"])
    job = await _dispatched_job(session, tenant, scheduled_contact, mission_setup)

    job = await svc.acknowledge(job.id)
    assert job.status == "ACKNOWLEDGED"

    with pytest.raises(Exception, match="Invalid observation job transition"):
        await svc.transition(job.id, "COMPLETED")  # skip chain -> invalid

    for state in ("PREPARING", "EXECUTING", "RECEIVING", "PROCESSING"):
        job = await svc.transition(job.id, state)
        assert job.status == state

    job = await svc.transition(job.id, "COMPLETED")
    assert job.status == "COMPLETED"
    assert job.completed_at is not None

    events = (
        await session.execute(
            select(OutboxEvent).where(
                OutboxEvent.aggregate_id == job.id,
                OutboxEvent.event_type == "OBSERVATION_JOB.COMPLETED",
            )
        )
    ).scalars().all()
    assert len(events) == 1
    assert events[0].payload["to_state"] == "COMPLETED"


async def test_receipt_completes_job_and_triggers_delivery(session, tenant, scheduled_contact, mission_setup):
    agent = await _registered_agent(session, mission_setup["station"].id)
    svc = AgentDispatchService(session, agent, mission_setup["station"])
    job = await _dispatched_job(session, tenant, scheduled_contact, mission_setup)
    job = await svc.acknowledge(job.id)
    for state in ("PREPARING", "EXECUTING", "RECEIVING", "PROCESSING"):
        job = await svc.transition(job.id, state)

    session.add(DataDeliveryDestination(
        org_id=tenant.org_id, type="webhook",
        config={"url": "https://demo.test/deliver"}, is_active=True,
    ))
    await session.flush()

    receipt = await svc.submit_receipt(
        job.id,
        ReceiptRequest(
            status="COMPLETED",
            actual_start=_now() - timedelta(minutes=4),
            actual_end=_now(),
            received_bytes=512_000.0,
            signal_quality={"snr_db": 18.2},
            notes="clean pass",
        ),
    )
    assert receipt.status == "COMPLETED"

    await session.refresh(job)
    assert job.status == "COMPLETED"

    receipts = (
        await session.execute(select(ExecutionReceipt).where(ExecutionReceipt.observation_job_id == job.id))
    ).scalars().all()
    assert len(receipts) == 1

    with pytest.raises(Exception, match="already submitted"):
        await svc.submit_receipt(job.id, ReceiptRequest(status="COMPLETED"))

    from models.data import DataDeliveryJob, Dataset

    deliveries = (
        await session.execute(
            select(DataDeliveryJob)
            .join(Dataset, Dataset.id == DataDeliveryJob.dataset_id)
            .where(Dataset.observation_job_id == job.id)
        )
    ).scalars().all()
    assert len(deliveries) == 1
    assert deliveries[0].status == "delivered"


async def test_cross_station_job_rejected(session, tenant, scheduled_contact, mission_setup):
    agent = await _registered_agent(session, mission_setup["station"].id)
    svc = AgentDispatchService(session, agent, mission_setup["station"])
    job = await _dispatched_job(session, tenant, scheduled_contact, mission_setup)

    from services.regulatory import RegulatoryAuthorizationService

    other = await RegulatoryAuthorizationService(session, tenant).register_station(
        code="ZA-OTHER-01", name="Other", country="South Africa",
        latitude=-33.9, longitude=18.6, altitude_m=100.0,
    )
    other_agent = await _registered_agent(session, other.id, "ag-other-01")
    other_svc = AgentDispatchService(session, other_agent, other)

    assert await other_svc.assigned_jobs() == []
    with pytest.raises(Exception, match="not found on this station"):
        await other_svc.get_job(job.id)


async def test_dispatch_due_jobs_transitions_queued(session, tenant, scheduled_contact, mission_setup):
    from services.orchestrator import ObservationOrchestrator

    orch = ObservationOrchestrator(session, tenant)
    job = await orch.create_job(scheduled_contact["contact"].id, mission_setup["profile"].id)
    for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED"):
        job = await orch.transition(job.id, state, actor="test")
    assert job.status == "QUEUED"

    dispatched = await dispatch_due_jobs(session, lead_s=24 * 3600)
    assert dispatched == 1
    await session.refresh(job)
    assert job.status == "DISPATCHED"


async def test_expired_certificate_rejects_identity(session, tenant, mission_setup):
    agent = await _registered_agent(
        session, mission_setup["station"].id, "ag-expired",
        certificate_valid_until=_now() - timedelta(days=1),
    )
    assert agent.status == "active"

    from services.agent_auth import get_agent_identity
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await get_agent_identity(db=session, x_client_cert_cn="ag-expired")
    assert exc.value.status_code == 401


# ── HTTP level ────────────────────────────────────────────────────────────────

@pytest.fixture
def agent_client():
    """TestClient over the real app; agent identity/chain pre-seeded in the DB."""
    app = main.app
    engine = create_async_engine(TEST_URL, poolclass=NullPool, pool_pre_ping=True)
    maker = async_sessionmaker(engine, expire_on_commit=False)

    async def _override_db():
        async with maker() as s:
            yield s

    app.dependency_overrides[get_db_session] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())


@pytest.fixture
def agent_chain():
    """Truncate + seed tenancy + build certified station/mission/contact + a
    DISPATCHED job + a registered agent identity (CN = ag-http-01)."""
    engine = create_async_engine(TEST_URL, poolclass=NullPool, pool_pre_ping=True)
    maker = async_sessionmaker(engine, expire_on_commit=False)

    async def _build():
        async with maker() as s:
            await _truncate_all(s)
            seed = await _seed_tenancy(s, PERMISSION_CODES)
            tenant = seed["tenant"]

            from models.spacecraft import Satellite, TLESet
            from models.mission import Spacecraft, Mission, MissionProfile, MissionRFProfile
            from models.station_twin import StationCapability, StationLicense
            from services.regulatory import RegulatoryAuthorizationService
            from conftest import TLE_L1, TLE_L2

            sat = Satellite(name="HTTP Sat", norad_id=90300, org_id=tenant.org_id)
            s.add(sat)
            await s.flush()
            s.add(TLESet(satellite_id=sat.id, line1=TLE_L1, line2=TLE_L2, epoch=_now(), is_active=True))
            sc = Spacecraft(name="HTTP SC", org_id=tenant.org_id, satellite_id=sat.id, norad_id=sat.norad_id)
            s.add(sc)
            await s.flush()
            mission = Mission(name="HTTP Mission", org_id=tenant.org_id, spacecraft_id=sc.id, status="active")
            s.add(mission)
            await s.flush()
            profile = MissionProfile(name="HTTP Profile", mission_id=mission.id, is_active=True)
            s.add(profile)
            await s.flush()
            s.add(MissionRFProfile(
                mission_profile_id=profile.id, band="UHF",
                uplink_frequency_hz=437_800_000.0, downlink_frequency_hz=145_825_000.0,
                max_tx_power_dbm=25.0, is_uplink_enabled=True, is_active=True,
            ))
            await s.flush()

            svc = RegulatoryAuthorizationService(s, tenant)
            station = await svc.register_station(
                code="ZA-HTTP-01", name="HTTP Station", country="South Africa",
                latitude=-33.9648, longitude=18.6085, altitude_m=160.0,
            )
            for state in ("PROVISIONING", "VALIDATING", "CERTIFIED"):
                await svc.transition_certification(station.id, state, state.lower())
            station.tx_enabled = True
            s.add(StationCapability(
                station_id=station.id, band="UHF",
                frequency_min_hz=430_000_000.0, frequency_max_hz=440_000_000.0,
                max_tx_power_dbm=25.0, tx_authorized=True, gain_dbi=12.0,
            ))
            s.add(StationLicense(
                station_id=station.id, license_type="uplink", issuing_authority="ICASA",
                license_number="HTTP-L1",
                frequency_bands=[{"min_hz": 430_000_000, "max_hz": 440_000_000}],
                max_power_dbm=25.0, issued_at=_now() - timedelta(days=1),
                expires_at=_now() + timedelta(days=30), status="valid",
            ))
            await s.commit()

            from services.contact_planning import ContactPlanningService

            planning = ContactPlanningService(s, tenant)
            visibilities = await planning.generate_visibility_opportunities(
                sc.id, [station.id], start=_now(), end=_now() + timedelta(hours=24),
            )
            opps = await planning.create_contact_opportunities([v.id for v in visibilities], profile.id)
            best = max((o for o in opps if o.status == "OPEN"), key=lambda o: o.opportunity_score or 0)
            reservation = await planning.create_reservation(
                best.id, tenant.org_id, spacecraft_id=sc.id, mission_id=mission.id,
            )
            reservation.status = "RESERVED"
            await s.flush()
            reservation = await planning.confirm_reservation(reservation.id)
            contact = await planning.schedule_contact(reservation.id)

            from services.orchestrator import ObservationOrchestrator

            orch = ObservationOrchestrator(s, tenant)
            job = await orch.create_job(contact.id, profile.id)
            for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED", "DISPATCHED"):
                job = await orch.transition(job.id, state, actor="http-test")

            from services.edge_agent import EdgeAgentService

            edge = EdgeAgentService(s, tenant)
            agent = await edge.register_agent(station.id, "ag-http-01", agent_version="2.0.0")
            agent.certificate_serial = "CRT-HTTP-01"
            agent.certificate_valid_until = _now() + timedelta(days=30)
            await s.commit()

            return {
                "job_id": job.id,
                "station_id": station.id,
                "agent_id": agent.agent_id,
                "org_id": tenant.org_id,
            }

    try:
        data = asyncio.run(_build())
    finally:
        asyncio.run(engine.dispose())
    return data


AGENT_HEADERS = {"X-Client-Cert-CN": "ag-http-01"}


def test_agent_auth_required(agent_client, agent_chain):
    assert agent_client.get("/api/v1/agent/jobs").status_code == 401
    unknown = agent_client.get("/api/v1/agent/jobs", headers={"X-Client-Cert-CN": "ag-nope"})
    assert unknown.status_code == 401


def test_agent_jobs_and_state_flow_over_http(agent_client, agent_chain):
    resp = agent_client.get("/api/v1/agent/jobs", headers=AGENT_HEADERS)
    assert resp.status_code == 200
    jobs = resp.json()["jobs"]
    assert len(jobs) == 1
    assert jobs[0]["job_id"] == str(agent_chain["job_id"])
    assert jobs[0]["status"] == "DISPATCHED"
    assert jobs[0]["rf"]["band"] == "UHF"

    job_url = f"/api/v1/agent/jobs/{agent_chain['job_id']}"
    assert agent_client.post(job_url + "/ack", headers=AGENT_HEADERS).json()["status"] == "ACKNOWLEDGED"

    for state in ("PREPARING", "EXECUTING", "RECEIVING", "PROCESSING"):
        resp = agent_client.post(job_url + "/state", headers=AGENT_HEADERS, json={"to_state": state})
        assert resp.status_code == 200
        assert resp.json()["status"] == state

    resp = agent_client.post(
        job_url + "/receipt",
        headers=AGENT_HEADERS,
        json={
            "status": "COMPLETED",
            "actual_start": _now().isoformat(),
            "actual_end": _now().isoformat(),
            "received_bytes": 65536.0,
            "signal_quality": {"snr_db": 17.5},
        },
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETED"

    dup = agent_client.post(job_url + "/receipt", headers=AGENT_HEADERS, json={"status": "COMPLETED"})
    assert dup.status_code == 409


def test_agent_telemetry_endpoints_over_http(agent_client, agent_chain):
    hb = agent_client.post("/api/v1/agent/heartbeat", headers=AGENT_HEADERS,
                           json={"agent_version": "2.0.0", "metrics": {"cpu_pct": 11}})
    assert hb.status_code == 200
    assert hb.json()["agent_id"] == "ag-http-01"

    ts = agent_client.post("/api/v1/agent/time-status", headers=AGENT_HEADERS,
                           json={"sync_status": "SYNCED", "offset_ms": 2.5})
    assert ts.status_code == 200
    assert ts.json()["sync_status"] == "SYNCED"

    tel = agent_client.post("/api/v1/agent/telemetry", headers=AGENT_HEADERS,
                            json={"telemetry_type": "signal", "payload": {"snr_db": 18.0}})
    assert tel.status_code == 200
    assert tel.json()["telemetry_type"] == "signal"


def test_agent_revoked_identity_rejected(agent_client, agent_chain):
    import asyncio as _aio
    from sqlalchemy.pool import NullPool as _NullPool

    engine = create_async_engine(TEST_URL, poolclass=_NullPool, pool_pre_ping=True)
    maker = async_sessionmaker(engine, expire_on_commit=False)

    async def _revoke():
        async with maker() as s:
            agent = (
                await s.execute(
                    select(StationAgentIdentity).where(StationAgentIdentity.agent_id == "ag-http-01")
                )
            ).scalars().first()
            agent.status = "revoked"
            agent.revoked_at = _now()
            await s.commit()

    _aio.run(_revoke())
    _aio.run(engine.dispose())

    resp = agent_client.get("/api/v1/agent/jobs", headers=AGENT_HEADERS)
    assert resp.status_code == 401


def test_agent_state_rejects_foreign_job(agent_client, agent_chain):
    resp = agent_client.post(
        f"/api/v1/agent/jobs/{uuid.uuid4()}/ack", headers=AGENT_HEADERS
    )
    assert resp.status_code == 404