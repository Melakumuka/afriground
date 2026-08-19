"""
Phase 2.4 â€” End-to-end edge simulation on the dev database.

Builds a fresh full chain (station -> satellite -> mission -> contact -> job),
registers an edge agent, then runs the orchestration runtime to drive the job
QUEUED -> COMPLETED while streaming heartbeat + telemetry, and finally executes
the data delivery pipeline. Produces a reproducible demo timeline.

Run from apps/api:
    $env:AFRIGROUND_SIM_URL="postgresql+asyncpg://afriground:afriground_dev_password@localhost:5433/afriground"
    & .venv\Scripts\python.exe scripts\simulate_edge.py
"""
import asyncio
import json
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import services.hooks  # noqa: F401  (registers publish hooks)

URL = __import__("os").environ.get(
    "AFRIGROUND_SIM_URL",
    "postgresql+asyncpg://afriground:afriground_dev_password@localhost:5433/afriground",
)

PERMISSION_CODES = [
    "platform.admin", "rbac.manage", "station.manage", "station.certify",
    "mission.manage", "contact.plan", "job.operate", "audit.view",
]

TLE_L1 = "1 25544U 98067A   24231.71854249  .00016717  00000-0  30870-3 0  9990"
TLE_L2 = "2 25544  51.6416 193.1427 0001806  61.0215 299.0943 15.50161160460789"

AGENT_ID = "sim-edge-01"

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


async def build_tenant(db):
    from models.core import Organization, Role, User
    from models.tenancy import Permission, RolePermission
    from services.tenancy import TenantContext

    org, _ = await get_or_create(
        db, Organization, slug="simulate-edge",
        defaults={"name": "Simulate Edge Co", "country": "South Africa", "is_active": True},
    )
    role, _ = await get_or_create(db, Role, name="Simulate Operator")
    perms = {}
    for code in PERMISSION_CODES:
        perm, _ = await get_or_create(db, Permission, code=code, defaults={"name": code})
        perms[code] = perm
        link = (
            await db.execute(select(RolePermission).filter_by(role_id=role.id, permission_id=perm.id))
        ).scalar_one_or_none()
        if not link:
            db.add(RolePermission(role_id=role.id, permission_id=perm.id))
    user, _ = await get_or_create(
        db, User, email="sim@afriground.demo",
        defaults={"id": uuid.uuid4(), "org_id": org.id, "role_id": role.id, "full_name": "Sim Operator",
                  "preferred_language": "en", "is_active": True},
    )
    if not user.org_id:
        user.org_id = org.id
        user.role_id = role.id
    await db.flush()
    return TenantContext(
        user=user, organization=org, roles=[role],
        permissions=set(PERMISSION_CODES), org_id=org.id,
    ), org


async def cleanup_previous_run(db) -> None:
    """Remove all data from previous simulation runs (dev-demo only)."""
    from sqlalchemy import text

    org = "(SELECT id FROM organizations WHERE slug = 'simulate-edge')"
    station = "(SELECT id FROM ground_stations WHERE code = 'ZA-SIM-01')"
    jobs = "(SELECT id FROM observation_jobs WHERE org_id IN " + org + ")"

    # Delivery pipeline
    await db.execute(text(
        "DELETE FROM data_delivery_jobs WHERE dataset_id IN "
        "(SELECT id FROM datasets WHERE observation_job_id IN " + jobs + ")"
    ))
    await db.execute(text("DELETE FROM datasets WHERE observation_job_id IN " + jobs))
    await db.execute(text("DELETE FROM data_delivery_destinations WHERE org_id IN " + org))
    # Job chain
    await db.execute(text("DELETE FROM execution_receipts WHERE observation_job_id IN " + jobs))
    await db.execute(text("DELETE FROM job_events WHERE observation_job_id IN " + jobs))
    await db.execute(text("DELETE FROM observation_jobs WHERE org_id IN " + org))
    await db.execute(text("DELETE FROM scheduled_contacts WHERE org_id IN " + org))
    await db.execute(text("DELETE FROM reservations WHERE org_id IN " + org))
    await db.execute(text("DELETE FROM contact_opportunities WHERE org_id IN " + org))
    await db.execute(text("DELETE FROM visibility_opportunities WHERE org_id IN " + org))
    # Station twin
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
    await db.execute(text("DELETE FROM ground_stations WHERE code = 'ZA-SIM-01'"))
    # Mission / spacecraft chain
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
    await db.execute(text("DELETE FROM tle_sets WHERE satellite_id IN (SELECT id FROM satellites WHERE norad_id = 90199)"))
    await db.execute(text("DELETE FROM satellites WHERE norad_id = 90199"))
    await db.commit()


async def run() -> None:
    engine = create_async_engine(URL, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as db:
            step("0. Cleaning previous simulation runs")
            await cleanup_previous_run(db)
            tenant, org = await build_tenant(db)

            # 1. Station: register -> certified
            step("1. Registering station ZA-SIM-01 and certifying")
            from services.regulatory import RegulatoryAuthorizationService
            svc = RegulatoryAuthorizationService(db, tenant)
            station = await svc.register_station(
                code="ZA-SIM-01", name="Sim Station", country="South Africa",
                latitude=-25.7479, longitude=28.2293, altitude_m=1370.0,
            )
            await svc.transition_certification(station.id, "PROVISIONING", "provision")
            await svc.transition_certification(station.id, "VALIDATING", "validate")
            await svc.transition_certification(station.id, "CERTIFIED", "certified")
            station.tx_enabled = True
            from models.station_twin import StationCapability, StationLicense
            db.add(StationCapability(
                station_id=station.id, band="UHF",
                frequency_min_hz=430_000_000.0, frequency_max_hz=440_000_000.0,
                max_tx_power_dbm=25.0, tx_authorized=True, gain_dbi=12.0,
            ))
            db.add(StationLicense(
                station_id=station.id, license_type="uplink", issuing_authority="ICASA",
                license_number="SIM-L1",
                frequency_bands=[{"min_hz": 430_000_000, "max_hz": 440_000_000}],
                max_power_dbm=25.0, issued_at=datetime.now(timezone.utc) - timedelta(days=1),
                expires_at=datetime.now(timezone.utc) + timedelta(days=30), status="valid",
            ))
            await db.commit()

            # 2. Spacecraft / mission chain
            step("2. Building satellite, spacecraft, mission, profiles")
            from models.spacecraft import Satellite, TLESet
            from models.mission import Spacecraft, Mission, MissionProfile, MissionRFProfile
            sat, _ = await get_or_create(db, Satellite, norad_id=90199, defaults={"name": "Sim Sat", "org_id": org.id})
            if not (await db.execute(select(TLESet).filter_by(satellite_id=sat.id))).scalars().first():
                db.add(TLESet(satellite_id=sat.id, line1=TLE_L1, line2=TLE_L2,
                              epoch=datetime.now(timezone.utc), is_active=True))
            sc, _ = await get_or_create(
                db, Spacecraft, norad_id=sat.norad_id,
                defaults={"name": "Sim SC", "org_id": org.id, "satellite_id": sat.id},
            )
            mission, _ = await get_or_create(
                db, Mission, spacecraft_id=sc.id, org_id=org.id,
                defaults={"name": "Sim Mission", "status": "active"},
            )
            profile, _ = await get_or_create(
                db, MissionProfile, mission_id=mission.id,
                defaults={"name": "Sim Profile", "is_active": True},
            )
            rf, _ = await get_or_create(
                db, MissionRFProfile, mission_profile_id=profile.id,
                defaults={"band": "UHF", "uplink_frequency_hz": 437_800_000.0,
                          "downlink_frequency_hz": 145_825_000.0, "max_tx_power_dbm": 25.0,
                          "is_uplink_enabled": True, "is_active": True},
            )
            await db.commit()

            # 3. Contact chain
            step("3. Adding delivery destinations")
            from models.data import DataDeliveryDestination
            existing_dests = (
                await db.execute(select(DataDeliveryDestination).where(DataDeliveryDestination.org_id == org.id))
            ).scalars().all()
            if not existing_dests:
                for i in range(2):
                    db.add(DataDeliveryDestination(
                        org_id=org.id, type="webhook",
                        config={"url": f"https://demo.afriground.space/deliver/{i}"}, is_active=True,
                    ))
                await db.flush()

            step("4. Planning visibility -> opportunity -> reservation -> scheduled contact")
            from services.contact_planning import ContactPlanningService
            planning = ContactPlanningService(db, tenant)
            now = datetime.now(timezone.utc)
            visibilities = await planning.generate_visibility_opportunities(
                sc.id, [station.id], start=now, end=now + timedelta(hours=24),
            )
            if not visibilities:
                raise RuntimeError("no visibility in the next 24h")
            opps = await planning.create_contact_opportunities(
                [v.id for v in visibilities], profile.id
            )
            open_opps = [o for o in opps if o.status == "OPEN"]
            best = max(open_opps, key=lambda o: o.opportunity_score or 0)
            reservation = await planning.create_reservation(
                best.id, org.id, spacecraft_id=sc.id, mission_id=mission.id,
            )
            reservation.status = "RESERVED"
            await db.flush()
            reservation = await planning.confirm_reservation(reservation.id)
            contact = await planning.schedule_contact(reservation.id)

            # 4. Job through planning transitions
            step("5. Creating observation job, driving to QUEUED")
            from services.orchestrator import ObservationOrchestrator
            orch = ObservationOrchestrator(db, tenant)
            job = await orch.create_job(contact.id, profile.id)
            for state in ("REQUESTED", "VALIDATING", "SCHEDULED", "QUEUED"):
                job = await orch.transition(job.id, state, actor="sim-user")

            # 5. Edge agent
            step("6. Registering edge agent + heartbeat + time-status")
            from services.edge_agent import EdgeAgentService
            edge = EdgeAgentService(db, tenant)
            await edge.register_agent(station.id, AGENT_ID, agent_version="1.4.2")
            await edge.report_heartbeat(station.id, AGENT_ID, "1.4.2", {"cpu_pct": 12, "uptime_s": 3600})
            await edge.report_time_status(station.id, AGENT_ID, "SYNCED", 4.0, "ntp")

            # 6. Run the runtime loop to completion
            step("7. Running orchestration runtime (simulate mode)")
            from models.contact import ObservationJob
            from services.orchestration_runtime import drain, process_observation_events
            steps = 0
            while job.status != "COMPLETED" and steps < 30:
                await drain(factory, limit=50)
                if job.status in ("EXECUTING", "RECEIVING", "PROCESSING"):
                    await edge.ingest_telemetry(
                        station.id, AGENT_ID, "signal", {"snr_db": 18.4 + steps * 0.1, "ber": 1e-6}
                    )
                    await edge.ingest_telemetry(
                        station.id, AGENT_ID, "power", {"main": True, "battery_pct": 98}
                    )
                    await edge.report_heartbeat(station.id, AGENT_ID, "1.4.2", {"phase": job.status})
                async with factory() as s2:
                    await process_observation_events(s2)
                async with factory() as s3:
                    job = await s3.get(ObservationJob, job.id)
                steps += 1
            assert job.status == "COMPLETED", f"job did not complete: {job.status}"
            step(f"Job COMPLETED after {steps} runtime cycles")

            # 7. Delivery pipeline
            step("8. Verifying data delivery pipeline")
            from services.delivery import DeliveryService
            deliveries = await DeliveryService(db).list_delivery_jobs(org.id)
            assert deliveries, "no delivery jobs created"
            for d in deliveries:
                assert d.status == "delivered" and d.checksum, f"delivery {d.id} not finalized"
            step(f"{len(deliveries)} delivery job(s) executed with checksums")

            # 8. Quality + watchdog demo
            step("9. Recomputing station quality")
            quality = await edge.recompute_quality(station.id)
            step(f"Quality score = {quality.score} (avail {quality.availability}, rel {quality.reliability}, time {quality.timeliness})")

            # 9. Watchdog: simulate a missed heartbeat
            step("10. Demonstrating missed-heartbeat watchdog")
            from models.station_twin import StationAgentIdentity
            from services.edge_agent import check_missed_heartbeats
            agent = (await db.execute(select(StationAgentIdentity).filter_by(agent_id=AGENT_ID))).scalars().first()
            agent.last_heartbeat_at = datetime.now(timezone.utc) - timedelta(minutes=10)
            await db.commit()
            flagged = await check_missed_heartbeats(db, threshold_s=60)
            step(f"Watchdog flagged {flagged} station(s); station status = {station.status}")
            await db.refresh(station)

            # 10. Metrics snapshot
            from services.orchestration_runtime import metrics
            m = await metrics(db)
            step("11. Outbox metrics: " + json.dumps(m["outbox"], default=str))

        print("\nâ”€â”€ Demo timeline â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")
        for t in timeline:
            print(f"  {t['t']}  {t['event']}")
        print("â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
