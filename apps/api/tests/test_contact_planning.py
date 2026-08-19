import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from models.contact import VisibilityOpportunity, ContactOpportunity, Reservation, ScheduledContact
from services.contact_planning import ContactPlanningService
from services.tenancy import TenantContext


async def test_generate_visibility_opportunities(session, tenant, mission_setup):
    planning = ContactPlanningService(session, tenant)
    vis = await planning.generate_visibility_opportunities(
        mission_setup["spacecraft"].id,
        [mission_setup["station"].id],
    )
    assert len(vis) >= 1
    assert all(v.status == "OPEN" for v in vis)
    assert all(v.max_elevation_deg >= 5.0 for v in vis)


async def test_create_contact_opportunities(session, tenant, mission_setup):
    planning = ContactPlanningService(session, tenant)
    vis = await planning.generate_visibility_opportunities(
        mission_setup["spacecraft"].id, [mission_setup["station"].id]
    )
    opps = await planning.create_contact_opportunities(
        [v.id for v in vis], mission_setup["profile"].id
    )
    assert len(opps) == len(vis)
    assert all(o.required_band == "UHF" for o in opps)
    assert any(o.status == "OPEN" for o in opps)


async def test_reservation_flow(session, tenant, mission_setup):
    planning = ContactPlanningService(session, tenant)
    vis = await planning.generate_visibility_opportunities(
        mission_setup["spacecraft"].id, [mission_setup["station"].id]
    )
    opps = await planning.create_contact_opportunities([v.id for v in vis], mission_setup["profile"].id)
    open_opps = [o for o in opps if o.status == "OPEN"]
    best = max(open_opps, key=lambda o: o.opportunity_score or 0)

    res = await planning.create_reservation(
        best.id, tenant.org_id, spacecraft_id=mission_setup["spacecraft"].id,
        mission_id=mission_setup["mission"].id,
    )
    assert res.status == "REQUESTED"

    res.status = "RESERVED"
    await session.flush()
    res = await planning.confirm_reservation(res.id)
    assert res.status == "CONFIRMED"


async def test_schedule_contact(session, tenant, scheduled_contact):
    contact = scheduled_contact["contact"]
    assert contact.status == "CONFIRMED"
    assert contact.scheduled_start < contact.scheduled_end
    assert contact.station_id == scheduled_contact["mission_setup"]["station"].id


async def test_reservation_requires_open_opportunity(session, tenant, mission_setup):
    planning = ContactPlanningService(session, tenant)
    vis = await planning.generate_visibility_opportunities(
        mission_setup["spacecraft"].id, [mission_setup["station"].id]
    )
    opps = await planning.create_contact_opportunities([v.id for v in vis], mission_setup["profile"].id)
    open_opps = [o for o in opps if o.status == "OPEN"]
    best = max(open_opps, key=lambda o: o.opportunity_score or 0)

    await planning.create_reservation(
        best.id, tenant.org_id, spacecraft_id=mission_setup["spacecraft"].id
    )
    # Opportunity is now RESERVED; second reservation must fail
    with pytest.raises(HTTPException) as exc:
        await planning.create_reservation(
            best.id, tenant.org_id, spacecraft_id=mission_setup["spacecraft"].id
        )
    assert exc.value.status_code == 409


async def test_plan_contact_returns_summary(session, tenant, mission_setup):
    planning = ContactPlanningService(session, tenant)
    summary = await planning.plan_contact(
        mission_setup["spacecraft"].id,
        mission_setup["profile"].id,
        tenant.org_id,
        [mission_setup["station"].id],
    )
    assert summary["visibility_opportunities"] >= 1
    assert summary["contact_opportunities"] >= 1
    assert "reservation_id" in summary