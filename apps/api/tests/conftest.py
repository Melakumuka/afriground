import asyncio
import os
import uuid
from datetime import datetime, timezone

import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from models import Base  # noqa: F401  (ensures metadata is fully loaded)
from models.core import Organization, Role, User
from models.tenancy import Permission, RolePermission
from services.tenancy import TenantContext

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

TEST_URL = (
    os.environ.get("AFRIGROUND_TEST_DATABASE_URL")
    or os.environ.get("DATABASE_URL")
    or "postgresql+asyncpg://localhost:5433/afriground_test"
)


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(TEST_URL, pool_pre_ping=True)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine):
    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as s:
        await _truncate_all(s)
        yield s


async def _truncate_all(session: AsyncSession) -> None:
    """Truncate every app table, preserving only alembic_version + spatial_ref_sys."""
    tables = (
        await session.execute(
            text(
                "SELECT tablename FROM pg_tables "
                "WHERE schemaname = 'public' "
                "AND tablename NOT IN ('alembic_version', 'spatial_ref_sys')"
            )
        )
    ).scalars().all()
    for t in tables:
        await session.execute(text(f'TRUNCATE TABLE "{t}" CASCADE'))
    await session.commit()


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


async def _seed_tenancy(session: AsyncSession, perm_codes: list[str]) -> dict:
    perms = {}
    for code in perm_codes:
        p = Permission(code=code, name=code)
        session.add(p)
        await session.flush()
        perms[code] = p

    role = Role(name="Test Platform Admin", is_system=True)
    session.add(role)
    await session.flush()
    for p in perms.values():
        session.add(RolePermission(role_id=role.id, permission_id=p.id))

    org = Organization(name="Test Org", slug=f"test-org-{uuid.uuid4().hex[:8]}", country="ZA", is_active=True)
    session.add(org)
    await session.flush()

    user = User(
        id=uuid.uuid4(),
        org_id=org.id,
        email=f"admin-{uuid.uuid4().hex[:8]}@test.local",
        full_name="Test Admin",
        role_id=role.id,
        preferred_language="en",
        is_active=True,
    )
    session.add(user)
    await session.flush()
    await session.commit()

    tenant = TenantContext(
        user=user,
        organization=org,
        roles=[role],
        permissions=set(perm_codes),
        org_id=org.id,
    )
    return {"tenant": tenant, "org": org, "user": user, "role": role, "perms": perms}


@pytest_asyncio.fixture
async def tenant(session):
    data = await _seed_tenancy(session, PERMISSION_CODES)
    return data["tenant"]


# ── Shared contact-chain fixtures ─────────────────────────────────────────────

TLE_L1 = "1 25544U 98067A   24231.71854249  .00016717  00000-0  30870-3 0  9990"
TLE_L2 = "2 25544  51.6416 193.1427 0001806  61.0215 299.0943 15.50161160460789"


@pytest_asyncio.fixture
async def mission_setup(session, tenant):
    """A certified station + spacecraft/mission/profile RF chain."""
    from datetime import datetime, timedelta, timezone
    from models.spacecraft import Satellite, TLESet
    from models.mission import (
        Spacecraft, Mission, MissionProfile, MissionRFProfile,
    )
    from models.station_twin import StationCapability, StationLicense, StationCertification
    from services.regulatory import RegulatoryAuthorizationService

    now = datetime.now(timezone.utc)

    sat = Satellite(name="Test Sat", norad_id=90001, org_id=tenant.org_id)
    session.add(sat)
    await session.flush()
    session.add(TLESet(satellite_id=sat.id, line1=TLE_L1, line2=TLE_L2, epoch=now, is_active=True))

    sc = Spacecraft(name="Test SC", org_id=tenant.org_id, satellite_id=sat.id, norad_id=sat.norad_id)
    session.add(sc)
    await session.flush()

    mission = Mission(name="Test Mission", org_id=tenant.org_id, spacecraft_id=sc.id, status="active")
    session.add(mission)
    await session.flush()

    profile = MissionProfile(name="Test Profile", mission_id=mission.id, is_active=True)
    session.add(profile)
    await session.flush()

    rf = MissionRFProfile(
        mission_profile_id=profile.id, band="UHF",
        uplink_frequency_hz=437_800_000.0, downlink_frequency_hz=145_825_000.0,
        max_tx_power_dbm=25.0, is_uplink_enabled=True, is_active=True,
    )
    session.add(rf)
    await session.flush()

    svc = RegulatoryAuthorizationService(session, tenant)
    station = await svc.register_station(
        code="ZA-TEST-02", name="Test Station 2", country="South Africa",
        latitude=-33.9648, longitude=18.6085, altitude_m=160.0,
    )
    await svc.transition_certification(station.id, "PROVISIONING", "p")
    await svc.transition_certification(station.id, "VALIDATING", "v")
    await svc.transition_certification(station.id, "CERTIFIED", "c")
    station.tx_enabled = True

    session.add(
        StationCapability(
            station_id=station.id, band="UHF",
            frequency_min_hz=430_000_000.0, frequency_max_hz=440_000_000.0,
            max_tx_power_dbm=25.0, tx_authorized=True, gain_dbi=12.0,
        )
    )
    session.add(
        StationLicense(
            station_id=station.id, license_type="uplink", issuing_authority="ICASA",
            license_number="L3", frequency_bands=[{"min_hz": 430_000_000, "max_hz": 440_000_000}],
            max_power_dbm=25.0, issued_at=now - timedelta(days=1),
            expires_at=now + timedelta(days=30), status="valid",
        )
    )
    await session.commit()

    return {
        "satellite": sat, "spacecraft": sc, "mission": mission,
        "profile": profile, "rf": rf, "station": station,
    }


@pytest_asyncio.fixture
async def scheduled_contact(session, tenant, mission_setup):
    """A CONFIRMED scheduled contact ready for job creation."""
    from datetime import datetime, timedelta, timezone
    from services.contact_planning import ContactPlanningService

    now = datetime.now(timezone.utc)
    planning = ContactPlanningService(session, tenant)
    visibilities = await planning.generate_visibility_opportunities(
        mission_setup["spacecraft"].id,
        [mission_setup["station"].id],
        start=now,
        end=now + timedelta(hours=24),
    )
    assert visibilities, "no visibility in the test window"

    vis_ids = [v.id for v in visibilities]
    opps = await planning.create_contact_opportunities(vis_ids, mission_setup["profile"].id)
    open_opps = [o for o in opps if o.status == "OPEN"]
    assert open_opps, "no feasible contact opportunities"

    best = max(open_opps, key=lambda o: o.opportunity_score or 0)
    reservation = await planning.create_reservation(
        best.id, tenant.org_id, spacecraft_id=mission_setup["spacecraft"].id,
        mission_id=mission_setup["mission"].id,
    )
    reservation.status = "RESERVED"
    await session.flush()
    reservation = await planning.confirm_reservation(reservation.id)
    contact = await planning.schedule_contact(reservation.id)

    return {
        "contact": contact,
        "reservation": reservation,
        "opportunity": best,
        "mission_setup": mission_setup,
    }