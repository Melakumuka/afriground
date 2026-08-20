"""
Idempotent demo seed for Phase 1 (tenancy, mission, station twin, contact chain, jobs).
Run from apps/api (credentials come from the gitignored repo-root `.env`:
    $env:AFRIGROUND_SEED_URL=$env:DATABASE_URL   # or set both in .env
    & .venv\Scripts\python.exe scripts\seed_phase1.py
"""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from scripts._env import database_url

URL = database_url("AFRIGROUND_SEED_URL")

PERMISSION_CODES = [
    "platform.admin",
    "rbac.manage",
    "station.manage",
    "station.certify",
    "mission.manage",
    "contact.plan",
    "job.operate",
    "audit.view",
    "api.manage",
]

ROLE_DEFS = {
    "Platform Admin": {"is_system": True, "permissions": PERMISSION_CODES},
    "GS Operator": {"is_system": True, "permissions": ["station.manage", "station.certify", "job.operate", "contact.plan"]},
    "Mission Manager": {"is_system": True, "permissions": ["mission.manage", "contact.plan", "job.operate"]},
    "Customer Admin": {"is_system": True, "permissions": ["mission.manage", "audit.view"]},
}


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
    print("Seeding roles & permissions...")
    perms = {}
    for code in PERMISSION_CODES:
        perm, _ = await get_or_create(db, __import__("models.tenancy", fromlist=["Permission"]).Permission, code=code)
        perms[code] = perm

    roles = {}
    for name, cfg in ROLE_DEFS.items():
        role, created = await get_or_create(db, __import__("models.core", fromlist=["Role"]).Role, name=name)
        if created:
            role.is_system = cfg["is_system"]
        roles[name] = role
        from models.tenancy import RolePermission
        for code in cfg["permissions"]:
            existing = (
                await db.execute(
                    select(RolePermission).filter_by(role_id=role.id, permission_id=perms[code].id)
                )
            ).scalar_one_or_none()
            if not existing:
                db.add(RolePermission(role_id=role.id, permission_id=perms[code].id))
    await db.flush()

    print("Seeding organizations & users...")
    from models.core import Organization, User
    demo_org, _ = await get_or_create(
        db, Organization, slug="afriground-demo",
        defaults={"name": "AfriGround Demo", "country": "South Africa", "is_active": True},
    )
    if demo_org.name != "AfriGround Demo":
        demo_org.name = "AfriGround Demo"
        demo_org.country = "South Africa"
        demo_org.is_active = True
    customer_org, _ = await get_or_create(
        db, Organization, slug="demo-customer",
        defaults={"name": "Demo Customer Co", "country": "Kenya", "is_active": True},
    )
    if customer_org.name != "Demo Customer Co":
        customer_org.name = "Demo Customer Co"
        customer_org.country = "Kenya"
        customer_org.is_active = True

    admin_user, _ = await get_or_create(
        db, User, email="admin@afriground.demo",
        defaults={"id": uuid.uuid4(), "org_id": demo_org.id, "role_id": roles["Platform Admin"].id,
                  "full_name": "Demo Admin", "preferred_language": "en", "is_active": True},
    )
    if not admin_user.org_id:
        admin_user.id = uuid.uuid4()
        admin_user.org_id = demo_org.id
        admin_user.role_id = roles["Platform Admin"].id
        admin_user.full_name = "Demo Admin"
        admin_user.is_active = True
    op_user, _ = await get_or_create(
        db, User, email="operator@afriground.demo",
        defaults={"id": uuid.uuid4(), "org_id": demo_org.id, "role_id": roles["GS Operator"].id,
                  "full_name": "Demo Operator", "preferred_language": "en", "is_active": True},
    )
    if not op_user.org_id:
        op_user.id = uuid.uuid4()
        op_user.org_id = demo_org.id
        op_user.role_id = roles["GS Operator"].id
        op_user.full_name = "Demo Operator"
        op_user.is_active = True
    cust_user, _ = await get_or_create(
        db, User, email="customer@afriground.demo",
        defaults={"id": uuid.uuid4(), "org_id": customer_org.id, "role_id": roles["Customer Admin"].id,
                  "full_name": "Demo Customer", "preferred_language": "en", "is_active": True},
    )
    if not cust_user.org_id:
        cust_user.id = uuid.uuid4()
        cust_user.org_id = customer_org.id
        cust_user.role_id = roles["Customer Admin"].id
        cust_user.full_name = "Demo Customer"
        cust_user.is_active = True

    print("Seeding satellite & spacecraft...")
    from models.spacecraft import Satellite, TLESet
    from models.mission import Spacecraft, Mission, MissionProfile, MissionRFProfile, MissionTelemetryDefinition, MissionTelecommandDefinition, MissionOperationalConstraint, MissionSLA

    satellite, _ = await get_or_create(
        db, Satellite, norad_id=25544,
        defaults={"name": "ISS (ZARYA)", "org_id": demo_org.id},
    )
    if satellite.name != "ISS (ZARYA)":
        satellite.name = "ISS (ZARYA)"
        satellite.org_id = demo_org.id
    tle, _ = await get_or_create(
        db, TLESet, satellite_id=satellite.id, is_active=True,
        defaults={
            "line1": "1 25544U 98067A   24231.71854249  .00016717  00000-0  30870-3 0  9990",
            "line2": "2 25544  51.6416 193.1427 0001806  61.0215 299.0943 15.50161160460789",
            "epoch": now,
            "source": "demo",
        },
    )
    if tle.line1 != "1 25544U 98067A   24231.71854249  .00016717  00000-0  30870-3 0  9990":
        tle.line1 = "1 25544U 98067A   24231.71854249  .00016717  00000-0  30870-3 0  9990"
        tle.line2 = "2 25544  51.6416 193.1427 0001806  61.0215 299.0943 15.50161160460789"
        tle.epoch = now
        tle.source = "demo"

    spacecraft, _ = await get_or_create(db, Spacecraft, name="ISS-Demo", org_id=demo_org.id)
    if not spacecraft.satellite_id:
        spacecraft.satellite_id = satellite.id
        spacecraft.norad_id = satellite.norad_id
        spacecraft.owner_org_id = demo_org.id
        spacecraft.status = "operational"

    mission, _ = await get_or_create(db, Mission, name="Demo LEO Observation", org_id=demo_org.id, spacecraft_id=spacecraft.id)
    if mission.mission_type != "earth_observation":
        mission.mission_type = "earth_observation"
        mission.description = "Phase 1 demo mission for contact planning and orchestration."
        mission.status = "active"
        mission.start_date = now - timedelta(days=30)
        mission.end_date = now + timedelta(days=300)

    profile, _ = await get_or_create(db, MissionProfile, name="Default Profile", mission_id=mission.id, version="1.0")
    if not profile.is_active:
        profile.is_active = True

    rf_profile, _ = await get_or_create(
        db, MissionRFProfile, mission_profile_id=profile.id, band="UHF",
        uplink_frequency_hz=437_800_000.0,
        downlink_frequency_hz=145_825_000.0,
        uplink_modulation="GMSK",
        downlink_modulation="AFSK",
        symbol_rate=9600.0,
        polarization="LHCP",
        max_tx_power_dbm=30.0,
        is_uplink_enabled=True,
        is_active=True,
    )
    await get_or_create(
        db, MissionTelemetryDefinition, mission_profile_id=profile.id,
        name="Battery Voltage", parameter_id="BAT_VOLT", data_type="float32",
        unit="V", bit_offset=0, bit_length=32, description="EPS battery voltage",
    )
    await get_or_create(
        db, MissionTelecommandDefinition, mission_profile_id=profile.id,
        name="Set Beacon Interval", command_code="CMD_SET_BEACON",
        parameters={"interval_s": "uint16"}, description="Change beacon interval",
    )
    await get_or_create(
        db, MissionOperationalConstraint, mission_id=mission.id,
        constraint_type="min_elevation", value={"min_deg": 10.0}, is_active=True,
    )
    await get_or_create(
        db, MissionSLA, mission_id=mission.id, sla_type="availability",
        target_value=95.0, unit="percent", reporting_window_days=30,
    )

    print("Seeding ground station via regulatory service...")
    from models.station import GroundStation
    from models.station_twin import StationCapability, StationHardware, StationLicense, StationQualityScore
    from services.tenancy import TenantContext
    from services.regulatory import RegulatoryAuthorizationService

    station = (
        await db.execute(select(GroundStation).where(GroundStation.code == "ZADEMO-01"))
    ).scalar_one_or_none()
    if not station:
        tenant = TenantContext(user=admin_user, organization=demo_org, org_id=demo_org.id)
        svc = RegulatoryAuthorizationService(db, tenant)
        station = await svc.register_station(
            code="ZADEMO-01",
            name="Cape Town Demo Station",
            country="South Africa",
            latitude=-33.9648,
            longitude=18.6085,
            altitude_m=160.0,
            operator_contact_email="ops@afriground.demo",
        )
        station.min_elevation_deg = 5.0
        station.antenna_diameter_m = 1.2
        station.supported_bands = ["UHF", "S"]
        await db.flush()
    else:
        print("  station ZADEMO-01 exists, skipping registration")

    await get_or_create(
        db, StationCapability, station_id=station.id, band="UHF",
        frequency_min_hz=430_000_000.0, frequency_max_hz=440_000_000.0,
        polarization="LHCP", max_tx_power_dbm=25.0, tx_authorized=True,
        gain_dbi=12.0, noise_figure_db=1.5,
    )
    await get_or_create(
        db, StationCapability, station_id=station.id, band="S",
        frequency_min_hz=2_200_000_000.0, frequency_max_hz=2_300_000_000.0,
        polarization="RHCP", tx_authorized=False, gain_dbi=18.0,
    )
    await get_or_create(
        db, StationHardware, station_id=station.id, hardware_type="antenna",
        model="Yaesu G-5500 + VHF/UHF Yagi", serial_number="ANT-0001",
        firmware_version="1.2.0", status="operational", installed_at=now - timedelta(days=90),
    )
    await get_or_create(
        db, StationLicense, station_id=station.id, license_type="uplink",
        issuing_authority="ICASA", license_number="ICASA-UPLINK-2026-0001",
        country="South Africa", frequency_bands=[{"min_hz": 430_000_000, "max_hz": 440_000_000}],
        max_power_dbm=25.0, issued_at=now - timedelta(days=60),
        expires_at=now + timedelta(days=305), status="valid",
    )
    await get_or_create(
        db, StationQualityScore, station_id=station.id, score=96.5,
        availability=98.2, reliability=97.1, timeliness=94.0,
        period_start=now - timedelta(days=30), period_end=now,
    )

    print("Seeding certification state machine...")
    cert = (
        await db.execute(
            select(__import__("models.station_twin", fromlist=["StationCertification"]).StationCertification)
            .where(__import__("models.station_twin", fromlist=["StationCertification"]).StationCertification.station_id == station.id)
            .order_by(__import__("models.station_twin", fromlist=["StationCertification"]).StationCertification.created_at.desc())
        )
    ).scalars().first()
    if cert and cert.current_state != "CERTIFIED":
        tenant = TenantContext(user=admin_user, organization=demo_org, org_id=demo_org.id)
        svc = RegulatoryAuthorizationService(db, tenant)
        await svc.transition_certification(station.id, "PROVISIONING", "Demo provisioning")
        await svc.transition_certification(station.id, "VALIDATING", "Demo validation")
        await svc.transition_certification(station.id, "CERTIFIED", "Demo certification")
        station.tx_enabled = True
        await db.flush()
        print("  station certified")

    print("Seeding contact chain (visibility -> opportunity -> reservation -> contact -> job)...")
    from services.contact_planning import ContactPlanningService
    from services.orchestrator import ObservationOrchestrator

    tenant = TenantContext(user=op_user, organization=demo_org, org_id=demo_org.id, permissions=set(PERMISSION_CODES))
    planning = ContactPlanningService(db, tenant)

    existing_job = (
        await db.execute(select(__import__("models.contact", fromlist=["ObservationJob"]).ObservationJob))
    ).scalars().first()
    if existing_job:
        print("  jobs already exist, skipping contact chain")
    else:
        visibilities = await planning.generate_visibility_opportunities(
            spacecraft.id, [station.id], start=now, end=now + timedelta(hours=24)
        )
        if visibilities:
            opportunities = await planning.create_contact_opportunities(
                [v.id for v in visibilities], profile.id
            )
            open_opps = [o for o in opportunities if o.status == "OPEN"]
            if open_opps:
                best = max(open_opps, key=lambda o: o.opportunity_score or 0)
                reservation = await planning.create_reservation(
                    best.id, customer_org.id, spacecraft_id=spacecraft.id, mission_id=mission.id
                )
                reservation.status = "RESERVED"
                await db.flush()
                reservation = await planning.confirm_reservation(reservation.id)
                contact = await planning.schedule_contact(reservation.id)
                orchestrator = ObservationOrchestrator(db, tenant)
                job = await orchestrator.create_job(
                    contact.id, profile.id, priority=5, tx_requested=False
                )
                print(f"  visibility={len(visibilities)} opportunities={len(opportunities)} job={job.id}")
        else:
            print("  no visibility in the next 24h for demo station; seeding visibility manually")
            vis = __import__("models.contact", fromlist=["VisibilityOpportunity"]).VisibilityOpportunity(
                org_id=demo_org.id, spacecraft_id=spacecraft.id, station_id=station.id,
                aos=now + timedelta(hours=2), los=now + timedelta(hours=2, minutes=8),
                max_elevation_deg=42.0, duration_seconds=480, status="OPEN",
            )
            db.add(vis)
            await db.flush()
            opportunities = await planning.create_contact_opportunities([vis.id], profile.id)
            open_opps = [o for o in opportunities if o.status == "OPEN"]
            if open_opps:
                best = max(open_opps, key=lambda o: o.opportunity_score or 0)
                reservation = await planning.create_reservation(
                    best.id, customer_org.id, spacecraft_id=spacecraft.id, mission_id=mission.id
                )
                reservation.status = "RESERVED"
                await db.flush()
                reservation = await planning.confirm_reservation(reservation.id)
                contact = await planning.schedule_contact(reservation.id)
                orchestrator = ObservationOrchestrator(db, tenant)
                job = await orchestrator.create_job(contact.id, profile.id, priority=5, tx_requested=False)
                print(f"  manual visibility job={job.id}")

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