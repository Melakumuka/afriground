"""
Idempotent demo enrichment (post-Phase 4.2): adds more missions, satellites,
stations, datasets, SLA violations, outbox events, and edge agents/time-status
so the deployed web UI's live feeds (mission control, data catalog, station
panel, network ranking) show a fuller, believable network.

Run from apps/api (credentials from the gitignored repo-root `.env`):
    $env:AFRIGROUND_SEED_URL=$env:DATABASE_URL   # or set both in .env
    & .venv\Scripts\python.exe scripts\seed_demo_rich.py
"""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from scripts._env import database_url

URL = database_url("AFRIGROUND_SEED_URL")


async def get_or_create(db, model_cls, defaults=None, **filters):
    stmt = select(model_cls).filter_by(**filters)
    row = (await db.execute(stmt)).scalars().first()
    if row:
        return row, False
    row = model_cls(**filters, **(defaults or {}))
    db.add(row)
    await db.flush()
    return row, True


async def seed(db):
    now = datetime.now(timezone.utc)
    from models.core import Organization
    from models.mission import Spacecraft, Mission
    from models.spacecraft import Satellite
    from models.data import Dataset
    from models.contact import ObservationJob
    from models.mission import SLASLAViolation
    from models.events import OutboxEvent
    from models.station import GroundStation
    from models.station_twin import StationQualityScore, StationCertification, StationAgentIdentity, StationTimeStatus

    demo_org = (
        await db.execute(select(Organization).where(Organization.slug == "afriground-demo"))
    ).scalar_one()

    print("Seeding additional satellites & missions...")
    extra_missions = [
        # norad, sat_name, tle_lines, spacecraft, mission, mission_type
        (
            33591,
            "NOAA-19 (NOAA)",
            (
                "1 33591U 09005A   24231.50000000  .00000120  00000-0  53566-4 0  9990",
                "2 33591  99.1680  45.4353 0014177  75.2728 285.0736 14.12887709  1314",
            ),
            "NOAA-Demo",
            "Atlantic Weather Relay",
            "weather",
        ),
        (
            40012,
            "SAOCOM 1A (GEOSAT)",
            (
                "1 40012U 14033A   24231.50000000  .00000110  00000-0  15000-3 0  9990",
                "2 40012  97.8840 178.2345 0000600  98.0000 262.0000 14.91536000  2030",
            ),
            "GEOSAT-Demo",
            "CropWatch Africa",
            "earth_observation",
        ),
    ]
    for norad, sat_name, tle, sc_name, mission_name, mtype in extra_missions:
        satellite, _ = await get_or_create(
            db, Satellite, norad_id=norad,
            defaults={"name": sat_name, "org_id": demo_org.id},
        )
        if satellite.name != sat_name:
            satellite.name = sat_name
            satellite.org_id = demo_org.id
        from models.spacecraft import TLESet
        await get_or_create(
            db, TLESet, satellite_id=satellite.id, is_active=True,
            defaults={"line1": tle[0], "line2": tle[1], "epoch": now, "source": "demo"},
        )
        spacecraft, _ = await get_or_create(db, Spacecraft, name=sc_name, org_id=demo_org.id)
        if not spacecraft.satellite_id:
            spacecraft.satellite_id = satellite.id
            spacecraft.norad_id = satellite.norad_id
            spacecraft.owner_org_id = demo_org.id
            spacecraft.status = "operational"
        mission, created = await get_or_create(
            db, Mission, name=mission_name, org_id=demo_org.id, spacecraft_id=spacecraft.id
        )
        if created:
            mission.mission_type = mtype
            mission.description = f"Demo {mtype} mission for live-feed enrichment."
            mission.status = "active"
            mission.start_date = now - timedelta(days=14)
            mission.end_date = now + timedelta(days=280)
        if mission.status != "active":
            mission.status = "active"

    print("Seeding SLA violations (live alert feed)...")
    demo_mission = (
        await db.execute(select(Mission).where(Mission.name == "Demo LEO Observation"))
    ).scalar_one()
    job = (
        await db.execute(select(ObservationJob).order_by(ObservationJob.created_at.asc()))
    ).scalars().first()
    violations = [
        ("VIOLATED", 92.4, now - timedelta(hours=2)),
        ("VIOLATED", 88.1, now - timedelta(days=1)),
        ("RESOLVED", 91.7, now - timedelta(days=3)),
    ]
    for status, actual, at in violations:
        await get_or_create(
            db, SLASLAViolation,
            mission_id=demo_mission.id, observation_job_id=job.id, sla_type="availability",
            actual_value=actual,
            defaults={
                "target_value": 95.0, "unit": "percent", "status": status,
                "violated_at": at,
            },
        )

    print("Seeding outbox events (orchestration metrics)...")
    outbox_seed = [
        ("mission.updated", "PUBLISHED", now - timedelta(hours=3), 2),
        ("contact.scheduled", "PUBLISHED", now - timedelta(hours=2), 1),
        ("job.completed", "PUBLISHED", now - timedelta(hours=1), 1),
        ("job.assigned", "PUBLISHED", now - timedelta(minutes=30), 1),
        ("contact.completed", "PENDING", now - timedelta(minutes=10), 1),
        ("telemetry.ingested", "PENDING", now - timedelta(minutes=2), 0),
    ]
    for event_type, status, created, attempts in outbox_seed:
        exists = (
            await db.execute(
                select(OutboxEvent).where(OutboxEvent.event_type == event_type, OutboxEvent.created_at == created)
            )
        ).scalar_one_or_none()
        if exists:
            continue
        db.add(
            OutboxEvent(
                aggregate_type="mission",
                aggregate_id=demo_mission.id,
                event_type=event_type,
                payload={"demo": True},
                status=status,
                created_at=created,
                published_at=created + timedelta(seconds=1) if status == "PUBLISHED" else None,
                attempt_count=attempts,
                next_retry_at=None if status == "PUBLISHED" else now + timedelta(minutes=5),
            )
        )
    await db.flush()

    print("Seeding datasets (data catalog)...")
    sat_rows = (await db.execute(select(Satellite))).scalars().all()
    datasets = [
        ("MULTISPECTRAL", "L1B_RAD", 12.5, now - timedelta(hours=5)),
        ("OPTICAL", "L0_RAW", 45.0, now - timedelta(hours=8)),
        ("SAR", "SLC", 0.0, now - timedelta(hours=26)),
        ("HYPERSPECTRAL", "L2A_CORRECTED", 5.2, now - timedelta(days=2)),
        ("MULTISPECTRAL", "L2A_CORRECTED", 22.0, now - timedelta(days=3)),
        ("OPTICAL", "L1B_RAD", 8.8, now - timedelta(days=4)),
    ]
    for idx, (sensor, product, cloud, acquired) in enumerate(datasets):
        sat = sat_rows[idx % len(sat_rows)]
        await get_or_create(
            db, Dataset, satellite_id=sat.id, sensor_type=sensor, product_type=product,
            cloud_cover=cloud,
            defaults={
                "processing_level": product,
                "acquisition_date": acquired,
                "storage_url": f"s3://afriground-free-repo/datasets/{sensor.lower()}-{product.lower()}-{acquired.strftime('%Y%m%d')}.tiff",
            },
        )

    print("Seeding additional stations + quality scores (network ranking)...")
    extra_stations = [
        ("ZADEMO-02", "Johannesburg Demo Station", "South Africa", -26.2041, 28.0473, 1750.0),
        ("ZADEMO-03", "Durban Demo Station", "South Africa", -29.8587, 31.0218, 8.0),
    ]
    for code, name, country, lat, lon, alt in extra_stations:
        station, created = await get_or_create(
            db, GroundStation, code=code,
            defaults={
                "org_id": demo_org.id, "name": name, "name_zh": name,
                "location": WKTElement(f"POINT({lon} {lat})", srid=4326),
                "latitude": lat, "longitude": lon, "altitude_m": alt,
                "country": country, "status": "operational",
                "certification_state": "CERTIFIED", "tx_enabled": True,
                "registration_date": now - timedelta(days=90),
            },
        )
        if station.certification_state != "CERTIFIED":
            station.certification_state = "CERTIFIED"
            station.tx_enabled = True
        await get_or_create(
            db, StationCertification, station_id=station.id, cert_type="operational",
            current_state="CERTIFIED",
            defaults={"created_at": now - timedelta(days=60)},
        )
        await get_or_create(
            db, StationQualityScore, station_id=station.id, period_end=now,
            defaults={
                "score": 91.0 if code == "ZADEMO-02" else 88.4,
                "availability": 96.0 if code == "ZADEMO-02" else 93.1,
                "reliability": 95.5 if code == "ZADEMO-02" else 92.2,
                "timeliness": 90.8 if code == "ZADEMO-02" else 89.0,
                "period_start": now - timedelta(days=30),
                "calculated_at": now,
            },
        )

    print("Seeding edge agents + time status (station panel)...")
    station_rows = (await db.execute(select(GroundStation))).scalars().all()
    station_agents = [
        ("ZADEMO-01", [("zademo-01-rf", "ser-9F2C1A"), ("zademo-01-power", "ser-7B1E93")]),
        ("ZADEMO-02", [("zademo-02-rf", "ser-4A2D77"), ("zademo-02-weather", "ser-8C3E12")]),
        ("ZADEMO-03", [("zademo-03-rf", "ser-5B8F40")]),
    ]
    agent_meta = {"zademo-01": "afriground-agent 1.4.2", "zademo-02": "afriground-agent 1.4.1", "zademo-03": "afriground-agent 1.4.0"}
    for station_row in station_rows:
        code = station_row.code
        entry = next((e for e in station_agents if e[0] == code), None)
        if not entry:
            continue
        version = agent_meta[code.lower()]
        for agent_id, serial in entry[1]:
            await get_or_create(
                db, StationAgentIdentity, station_id=station_row.id, agent_id=agent_id,
                defaults={
                    "agent_version": version, "certificate_serial": serial,
                    "certificate_valid_until": now + timedelta(days=340),
                    "last_heartbeat_at": now - timedelta(seconds=45),
                    "status": "active",
                },
            )
        offsets = [3.2, 180.0] if code == "ZADEMO-01" else [5.8, 96.4] if code == "ZADEMO-02" else [12.1]
        for offset in offsets:
            await get_or_create(
                db, StationTimeStatus, station_id=station_row.id, sync_status="SYNCED" if offset < 100 else "DEGRADED",
                offset_ms=offset,
                defaults={
                    "last_sync_at": now - timedelta(minutes=4) if offset < 100 else now - timedelta(hours=6),
                    "clock_source": "ntp", "reported_at": now - timedelta(seconds=45),
                },
            )

    print("Seed complete.")


async def main():
    engine = create_async_engine(URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: None)  # ensure connectivity
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as db:
        await seed(db)
        await db.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())