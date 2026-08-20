"""
Phase 4.0 — Real edge agent demo on the dev database.

Builds the full chain (station -> mission -> contact -> job), registers an
mTLS agent identity, dispatches the job to the edge, and drives it through the
real agent contract (fetch assigned jobs -> ack -> execution chain -> receipt)
while streaming heartbeat + time-status + telemetry. Data delivery runs on
COMPLETED exactly like in the API path.

The agent-side steps go through AgentDispatchService — the same service the
`/api/v1/agent/*` routes expose over mTLS — so this is the reference flow for
the afriground-station-agent client.

Run from apps/api (credentials come from the gitignored repo-root `.env`:
    $env:AFRIGROUND_SIM_URL=$env:DATABASE_URL   # or set both in .env
    & .venv\Scripts\python.exe scripts\agent_sim.py
"""
import asyncio
import json
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import services.hooks  # noqa: F401  (registers publish hooks)
from scripts._env import database_url

URL = database_url("AFRIGROUND_SIM_URL")

AGENT_ID = "sim-edge-01"

TLE_L1 = "1 25544U 98067A   24231.71854249  .00016717  00000-0  30870-3 0  9990"
TLE_L2 = "2 25544  51.6416 193.1427 0001806  61.0215 299.0943 15.50161160460789"

timeline = []


def step(msg: str) -> None:
    timeline.append({"t": datetime.now(timezone.utc).isoformat(), "event": msg})
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}")


async def get_or_create(db, model_cls, defaults=None, **filters):
    row = (await db.execute(select(model_cls).filter_by(**filters))).scalars().first()
    if row:
        return row, False
    row = model_cls(**filters, **(defaults or {}))
    db.add(row)
    await db.flush()
    return row, True


async def cleanup_previous_run(db) -> None:
    from sqlalchemy import text

    org = "(SELECT id FROM organizations WHERE slug = 'agent-demo')"
    station = "(SELECT id FROM ground_stations WHERE code = 'ZA-AGENT-01')"
    jobs = "(SELECT id FROM observation_jobs WHERE org_id IN " + org + ")"

    await db.execute(text(
        "DELETE FROM data_delivery_jobs WHERE dataset_id IN "
        "(SELECT id FROM datasets WHERE observation_job_id IN " + jobs + ")"
    ))
    await db.execute(text("DELETE FROM datasets WHERE observation_job_id IN " + jobs))
    await db.execute(text("DELETE FROM data_delivery_destinations WHERE org_id IN " + org))
    await db.execute(text("DELETE FROM execution_receipts WHERE observation_job_id IN " + jobs))
    await db.execute(text("DELETE FROM job_events WHERE observation_job_id IN " + jobs))
    await db.execute(text("DELETE FROM observation_jobs WHERE org_id IN " + org))
    await db.execute(text("DELETE FROM scheduled_contacts WHERE org_id IN " + org))
    await db.execute(text("DELETE FROM reservations WHERE org_id IN " + org))
    await db.execute(text("DELETE FROM contact_opportunities WHERE org_id IN " + org))
    await db.execute(text("DELETE FROM visibility_opportunities WHERE org_id IN " + org))
    await db.execute(text("DELETE FROM station_heartbeats WHERE station_id IN " + station))
    await db.execute(text("DELETE FROM station_telemetry_readings WHERE station_id IN " + station))
    await db.execute(text("DELETE FROM station_time_statuses WHERE station_id IN " + station))
    await db.execute(text("DELETE FROM station_quality_scores WHERE station_id IN " + station))
    await db.execute(text("DELETE FROM station_agent_identities WHERE station_id IN " + station))
    await db.execute(text("DELETE FROM station_certification_events WHERE station_id IN " + station))
    await db.execute(text("DELETE FROM station_certifications WHERE station_id IN " + station))
    await db.execute(text("DELETE FROM station_capabilities WHERE station_id IN " + station))
    await db.execute(text("DELETE FROM station_licenses WHERE station_id IN " + station))
    await db.execute(text("DELETE FROM incidents WHERE station_id IN " + station))
    await db.execute(text("DELETE FROM ground_stations WHERE code = 'ZA-AGENT-01'"))
    await db.execute(text("DELETE FROM sla_violations WHERE mission_id IN "
                          "(SELECT id FROM missions WHERE spacecraft_id IN "
                          "(SELECT id FROM spacecraft WHERE org_id IN " + org + "))"))
    await db.execute(text("DELETE FROM mission_rf_profiles WHERE mission_profile_id IN "
                          "(SELECT id FROM mission_profiles WHERE mission_id IN "
                          "(SELECT id FROM missions WHERE spacecraft_id IN "
                          "(SELECT id FROM spacecraft WHERE org_id IN " + org + ")))"))
    await db.execute(text("DELETE FROM mission_profiles WHERE mission_id IN "
                          "(SELECT id FROM missions WHERE spacecraft_id IN "
                          "(SELECT id FROM spacecraft WHERE org_id IN " + org + "))"))
    await db.execute(text("DELETE FROM missions WHERE spacecraft_id IN "
                          "(SELECT id FROM spacecraft WHERE org_id IN " + org + ")"))
    await db.execute(text("DELETE FROM spacecraft WHERE org_id IN " + org))
    await db.execute(text("DELETE FROM tle_sets WHERE satellite_id IN (SELECT id FROM satellites WHERE norad_id = 90200)"))
    await db.execute(text("DELETE FROM satellites WHERE norad_id = 90200"))
    await db.commit()


async def build_tenant(db):
    from models.core import Organization, Role, User
    from models.tenancy import Permission, RolePermission
    from services.tenancy import TenantContext

    org, _ = await get_or_create(
        db, Organization, slug="agent-demo",
        defaults={"name": "Agent Demo Co", "country": "South Africa", "is_active": True},
    )
    role, _ = await get_or_create(db, Role, name="Agent Demo Operator")
    for code in ["platform.admin", "station.manage", "mission.manage",
                 "contact.plan", "job.operate", "api.manage"]:
        perm, _ = await get_or_create(db, Permission, code=code, defaults={"name": code})
        link = (await db.execute(select(RolePermission).filter_by(role_id=role.id, permission_id=perm.id))).scalar_one_or_none()
        if not link:
            db.add(RolePermission(role_id=role.id, permission_id=perm.id))
    user, _ = await get_or_create(
        db, User, email="agent@afriground.demo",
        defaults={"id": uuid.uuid4(), "org_id": org.id, "role_id": role.id,
                  "full_name": "Agent Demo Operator", "preferred_language": "en", "is_active": True},
    )
    if not user.org_id:
        user.org_id = org.id
        user.role_id = role.id
    await db.flush()
    return TenantContext(
        user=user, organization=org, roles=[role],
        permissions=set(["platform.admin", "station.manage", "mission.manage",
                         "contact.plan", "job.operate", "api.manage"]),
        org_id=org.id,
    ), org


async def run() -> None:
    engine = create_async_engine(URL, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as db:
            step("0. Cleaning previous agent-demo runs")
            await cleanup_previous_run(db)
            tenant, org = await build_tenant(db)

            # 1. Station certified
            step("1. Registering station ZA-AGENT-01 and certifying")
            from services.regulatory import RegulatoryAuthorizationService
            svc = RegulatoryAuthorizationService(db, tenant)
            station = await svc.register_station(
                code="ZA-AGENT-01", name="Agent Demo Station", country="South Africa",
                latitude=-25.7479, longitude=28.2293, altitude_m=1370.0,
            )
            for state in ("PROVISIONING", "VALIDATING", "CERTIFIED"):
                await svc.transition_certification(station.id, state, state.lower())
            station.tx_enabled = True
            from models.station_twin import StationCapability, StationLicense
            db.add(StationCapability(
                station_id=station.id, band="UHF",
                frequency_min_hz=430_000_000.0, frequency_max_hz=440_000_000.0,
                max_tx_power_dbm=25.0, tx_authorized=True, gain_dbi=12.0,
            ))
            db.add(StationLicense(
                station_id=station.id, license_type="uplink", issuing_authority="ICASA",
                license_number="AGENT-L1",
                frequency_bands=[{"min_hz": 430_000_000, "max_hz": 440_000_000}],
                max_power_dbm=25.0, issued_at=datetime.now(timezone.utc) - timedelta(days=1),
                expires_at=datetime.now(timezone.utc) + timedelta(days=30), status="valid",
            ))
            await db.commit()

            # 2. Satellite / mission chain
            step("2. Building satellite, spacecraft, mission, profiles")
            from models.spacecraft import Satellite, TLESet
            from models.mission import Spacecraft, Mission, MissionProfile, MissionRFProfile
            sat, _ = await get_or_create(db, Satellite, norad_id=90200, defaults={"name": "Agent Sat", "org_id": org.id})
            if not (await db.execute(select(TLESet).filter_by(satellite_id=sat.id))).scalars().first():
                db.add(TLESet(satellite_id=sat.id, line1=TLE_L1, line2=TLE_L2,
                              epoch=datetime.now(timezone.utc), is_active=True))
            sc, _ = await get_or_create(
                db, Spacecraft, norad_id=sat.norad_id,
                defaults={"name": "Agent SC", "org_id": org.id, "satellite_id": sat.id},
            )
            mission, _ = await get_or_create(
                db, Mission, spacecraft_id=sc.id, org_id=org.id,
                defaults={"name": "Agent Mission", "status": "active"},
            )
            profile, _ = await get_or_create(
                db, MissionProfile, mission_id=mission.id,
                defaults={"name": "Agent Profile", "is_active": True},
            )
            await get_or_create(
                db, MissionRFProfile, mission_profile_id=profile.id,
                defaults={"band": "UHF", "uplink_frequency_hz": 437_800_000.0,
                          "downlink_frequency_hz": 145_825_000.0, "max_tx_power_dbm": 25.0,
                          "is_uplink_enabled": True, "is_active": True},
            )
            await db.commit()

            # 3. Delivery destinations + contact chain
            step("3. Planning contact + adding delivery destinations")
            from models.data import DataDeliveryDestination
            if not (await db.execute(select(DataDeliveryDestination).where(DataDeliveryDestination.org_id == org.id))).scalars().all():
                db.add(DataDeliveryDestination(
                    org_id=org.id, type="webhook",
                    config={"url": "https://demo.afriground.space/deliver/agent"}, is_active=True,
                ))
                await db.flush()

            from services.contact_planning import ContactPlanningService
            planning = ContactPlanningService(db, tenant)
            now = datetime.now(timezone.utc)
            visibilities = await planning.generate_visibility_opportunities(
                sc.id, [station.id], start=now, end=now + timedelta(hours=24),
            )
            if not visibilities:
                raise RuntimeError("no visibility in the next 24h")
            opps = await planning.create_contact_opportunities([v.id for v in visibilities], profile.id)
            best = max((o for o in opps if o.status == "OPEN"), key=lambda o: o.opportunity_score or 0)
            reservation = await planning.create_reservation(
                best.id, org.id, spacecraft_id=sc.id, mission_id=mission.id,
            )
            reservation.status = "RESERVED"
            await db.flush()
            reservation = await planning.confirm_reservation(reservation.id)
            contact = await planning.schedule_contact(reservation.id)

            # 4. Job to QUEUED; pull the contact into the dispatch window
            step("4. Creating observation job, driving to QUEUED")
            from services.orchestrator import ObservationOrchestrator
            orch = ObservationOrchestrator(db, tenant)
            job = await orch.create_job(contact.id, profile.id)
            for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED"):
                job = await orch.transition(job.id, state, actor="agent-demo")
            contact.scheduled_start = now + timedelta(minutes=2)
            contact.scheduled_end = now + timedelta(minutes=8)
            await db.commit()

            # 5. Agent identity (CN == agent_id, as issued by gen_agent_certs.py)
            step("5. Registering agent identity (mTLS CN = %s)" % AGENT_ID)
            from services.edge_agent import EdgeAgentService
            edge = EdgeAgentService(db, tenant)
            agent = await edge.register_agent(
                station.id, AGENT_ID, agent_version="2.0.0",
                public_key_pem="",
            )
            agent.certificate_serial = "AGENT-SIM-01"
            agent.certificate_valid_until = datetime.now(timezone.utc) + timedelta(days=365)
            await db.commit()

            # 6. System dispatcher: QUEUED -> DISPATCHED (lead reached)
            step("6. Orchestrator dispatch (lead window reached)")
            from services.orchestration_runtime import dispatch_due_jobs
            dispatched = await dispatch_due_jobs(db, lead_s=3600)
            assert dispatched == 1, f"expected 1 dispatch, got {dispatched}"
            await db.refresh(job)
            step(f"Job {job.status} — waiting for agent")

            # 7. Agent contract (same service the /api/v1/agent routes use)
            step("7. Agent fetches assigned jobs")
            from services.agent_dispatch import AgentDispatchService
            dispatch = AgentDispatchService(db, agent, station)
            jobs = await dispatch.assigned_jobs()
            assert jobs and jobs[0].id == job.id, "agent did not receive the dispatched job"
            bundle = await dispatch.job_bundle(jobs[0])
            step(f"Job bundle: contact {bundle['scheduled_contact']['start']} -> {bundle['scheduled_contact']['end']}, band {bundle['rf']['band']}")

            step("8. Agent heartbeats + time-status + telemetry (mTLS endpoints)")
            await edge.report_heartbeat(station.id, AGENT_ID, "2.0.0", {"cpu_pct": 9, "uptime_s": 86400})
            await edge.report_time_status(station.id, AGENT_ID, "SYNCED", 3.2, "ntp")
            await edge.ingest_telemetry(station.id, AGENT_ID, "signal", {"snr_db": 17.9, "ber": 8e-7})

            step("9. Agent ACKs and drives the execution chain")
            job = await dispatch.acknowledge(job.id)
            step(f"  ACKNOWLEDGED ({job.status})")
            for state in ("PREPARING", "EXECUTING", "RECEIVING", "PROCESSING"):
                job = await dispatch.transition(job.id, state)
                step(f"  {state}")
                if state in ("EXECUTING", "RECEIVING"):
                    await edge.ingest_telemetry(station.id, AGENT_ID, "signal", {"snr_db": 19.1})
                    await edge.report_heartbeat(station.id, AGENT_ID, "2.0.0", {"phase": state})

            step("10. Agent submits execution receipt")
            from services.agent_dispatch import ReceiptRequest
            receipt = await dispatch.submit_receipt(
                job.id,
                ReceiptRequest(
                    status="COMPLETED",
                    actual_start=contact.scheduled_start,
                    actual_end=contact.scheduled_start + timedelta(minutes=5),
                    received_bytes=1_048_576.0,
                    recorded_file_url="minio://afriground-raw/observations/agent-demo/raw.bin",
                    signal_quality={"snr_db": 19.1, "ber": 8e-7},
                    notes="clean pass",
                ),
            )
            await db.refresh(job)
            step(f"Receipt {receipt.status}; job {job.status}")

            # 8. Delivery ran on COMPLETED
            step("11. Verifying data delivery pipeline")
            from services.delivery import DeliveryService
            deliveries = await DeliveryService(db).list_delivery_jobs(org.id)
            assert deliveries and deliveries[0].status == "delivered", "delivery not executed"
            step(f"{len(deliveries)} delivery job(s) executed with checksums")

            # 9. Watchdog check (agent is fresh -> no flag)
            step("12. Missed-heartbeat watchdog sweep")
            from services.edge_agent import check_missed_heartbeats
            flagged = await check_missed_heartbeats(db, threshold_s=60)
            step(f"Watchdog flagged {flagged} station(s)")

            step("DONE — agent lifecycle complete")

        print("\n----- Agent demo timeline -----")
        for t in timeline:
            print(f"  {t['t']}  {t['event']}")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())