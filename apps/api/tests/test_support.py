"""
Phase 4.2 tests — support ticket lifecycle via the SupportEngine.
"""
import uuid

from sqlalchemy import select

from models.core import User
from models.data import SupportTicket
from services.support_engine import SupportEngine, TicketCreateRequest


async def _reporter(session, org_id):
    user = User(
        id=uuid.uuid4(),
        org_id=org_id,
        email=f"reporter-{uuid.uuid4()}@test.dev",
        full_name="Ticket Reporter",
    )
    session.add(user)
    await session.flush()
    return user


async def test_create_ticket_records_reporter_and_category(session, tenant):
    reporter = await _reporter(session, tenant.org_id)
    engine = SupportEngine(session)

    resp = await engine.create_ticket(
        TicketCreateRequest(
            org_id=tenant.org_id,
            category="technical",
            priority="high",
            subject="Bad pass",
            description="AOS was late",
        ),
        reporter.id,
    )

    assert resp.category == "technical"
    assert resp.priority == "high"
    assert resp.status == "open"
    assert resp.subject == "Bad pass"

    row = (
        await session.execute(select(SupportTicket).where(SupportTicket.id == resp.id))
    ).scalar_one()
    assert row.reporter_id == reporter.id
    assert row.org_id == tenant.org_id


async def test_list_tickets_scoped_to_org(session, tenant):
    reporter = await _reporter(session, tenant.org_id)
    engine = SupportEngine(session)
    await engine.create_ticket(
        TicketCreateRequest(
            org_id=tenant.org_id,
            category="billing",
            priority="normal",
            subject="Invoice",
            description="Late invoice",
        ),
        reporter.id,
    )
    await engine.create_ticket(
        TicketCreateRequest(
            org_id=tenant.org_id,
            category="scheduling",
            priority="urgent",
            subject="Slot conflict",
            description="Slot overlap",
        ),
        reporter.id,
    )

    tickets = await engine.list_tickets(tenant.org_id)
    assert len(tickets) == 2
    assert {t.category for t in tickets} == {"billing", "scheduling"}