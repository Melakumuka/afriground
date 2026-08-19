"""
Phase 3.2 tests — network routing scoring and operational constraints in
contact planning.
"""
from datetime import datetime, timedelta, timezone

from models.mission import MissionOperationalConstraint
from models.station_twin import StationHeartbeat, StationQualityScore
from services.contact_planning import ContactPlanningService
from services.network_routing import NetworkRoutingService


async def _add_quality(session, station_id, score, age_minutes=0):
    now = datetime.now(timezone.utc)
    session.add(
        StationQualityScore(
            station_id=station_id,
            score=score,
            availability=score,
            reliability=score,
            timeliness=score,
            period_start=now - timedelta(hours=1),
            period_end=now,
            calculated_at=now - timedelta(minutes=age_minutes),
        )
    )
    await session.flush()


async def _add_heartbeat(session, station_id, age_minutes=0):
    now = datetime.now(timezone.utc)
    session.add(
        StationHeartbeat(
            station_id=station_id,
            agent_id="test-agent",
            metrics={},
            received_at=now - timedelta(minutes=age_minutes),
        )
    )
    await session.flush()


async def test_score_station_blends_factors(session, tenant, mission_setup):
    station = mission_setup["station"]

    # Certified but no quality, stale heartbeat.
    baseline = await NetworkRoutingService(session).score_station(station.id)
    assert baseline["certified"] is True
    assert baseline["heartbeat_fresh"] is False
    assert 0 <= baseline["composite_score"] <= 100

    # Add fresh heartbeat + high quality -> strictly better.
    await _add_quality(session, station.id, 99.0)
    await _add_heartbeat(session, station.id, age_minutes=1)
    await session.commit()

    improved = await NetworkRoutingService(session).score_station(station.id)
    assert improved["heartbeat_fresh"] is True
    assert improved["quality_score"] == 99.0
    assert improved["composite_score"] > baseline["composite_score"]
    assert "high-quality" in improved["reasons"]


async def test_rank_network_sorts_descending(session, tenant, mission_setup):
    svc = NetworkRoutingService(session)
    ranked = await svc.rank_network()
    scores = [r["composite_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


async def test_opportunity_score_includes_routing_bonus(session, tenant, scheduled_contact):
    from sqlalchemy import select
    from models.contact import ContactOpportunity

    opp = scheduled_contact["opportunity"]
    station_id = scheduled_contact["contact"].station_id

    await _add_quality(session, station_id, 100.0)
    await _add_heartbeat(session, station_id, age_minutes=1)
    await session.commit()

    bonus = await NetworkRoutingService(session).station_bonus(station_id)
    assert 0 < bonus <= 10

    rows = (
        await session.execute(
            select(ContactOpportunity).where(ContactOpportunity.id == opp.id)
        )
    ).scalars().first()
    assert rows.opportunity_score >= bonus  # routing contribution present


async def test_station_restriction_constraint_closes_opportunities(
    session, tenant, mission_setup, scheduled_contact
):
    from datetime import datetime, timedelta, timezone

    mission = mission_setup["mission"]
    session.add(
        MissionOperationalConstraint(
            mission_id=mission.id,
            constraint_type="station_restriction",
            value={"station_ids": ["00000000-0000-0000-0000-000000000001"]},
            is_active=True,
        )
    )
    await session.commit()

    planning = ContactPlanningService(session, tenant)
    now = datetime.now(timezone.utc)
    visibilities = await planning.generate_visibility_opportunities(
        mission_setup["spacecraft"].id,
        [mission_setup["station"].id],
        start=now,
        end=now + timedelta(hours=12),
    )
    vis_ids = [v.id for v in visibilities]
    opps = await planning.create_contact_opportunities(vis_ids, mission_setup["profile"].id)

    assert opps
    assert all(o.status == "CLOSED" for o in opps)


async def test_min_elevation_constraint_closes_low_passes(
    session, tenant, mission_setup
):
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import select
    from models.contact import ContactOpportunity

    mission = mission_setup["mission"]
    session.add(
        MissionOperationalConstraint(
            mission_id=mission.id,
            constraint_type="min_elevation",
            value={"min_elevation_deg": 90.0},
            is_active=True,
        )
    )
    await session.commit()

    planning = ContactPlanningService(session, tenant)
    now = datetime.now(timezone.utc)
    visibilities = await planning.generate_visibility_opportunities(
        mission_setup["spacecraft"].id,
        [mission_setup["station"].id],
        start=now,
        end=now + timedelta(hours=12),
    )
    vis_ids = [v.id for v in visibilities]
    opps = await planning.create_contact_opportunities(vis_ids, mission_setup["profile"].id)

    assert opps
    assert all(o.status == "CLOSED" for o in opps)