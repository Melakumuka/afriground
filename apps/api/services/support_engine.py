"""
Support Engine — Customer Ticketing & Support operations.
"""
import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from pydantic import BaseModel

from models.data import SupportTicket


# ── Schemas ──────────────────────────────────────────────────────────────────

class TicketCreateRequest(BaseModel):
    org_id: uuid.UUID
    category: str  # billing, technical, scheduling, hardware
    priority: str  # low, normal, high, urgent
    subject: str
    description: str

class TicketResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    category: str
    priority: str
    status: str
    subject: str
    description: str
    created_at: Optional[datetime] = None


# ── Service ──────────────────────────────────────────────────────────────────

class SupportEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_ticket(self, req: TicketCreateRequest, reporter_id: uuid.UUID) -> TicketResponse:
        """Open a new support ticket."""
        ticket = SupportTicket(
            org_id=req.org_id,
            reporter_id=reporter_id,
            category=req.category,
            priority=req.priority,
            status="open",
            subject=req.subject,
            description=req.description,
        )
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)

        return TicketResponse(
            id=ticket.id,
            org_id=ticket.org_id,
            category=ticket.category,
            priority=ticket.priority,
            status=ticket.status,
            subject=ticket.subject,
            description=ticket.description,
            created_at=ticket.created_at,
        )

    async def list_tickets(self, org_id: uuid.UUID) -> List[TicketResponse]:
        """List all tickets for an organization."""
        stmt = select(SupportTicket).where(SupportTicket.org_id == org_id).order_by(SupportTicket.created_at.desc())
        result = await self.db.execute(stmt)
        tickets = result.scalars().all()

        return [
            TicketResponse(
                id=t.id,
                org_id=t.org_id,
                category=t.category,
                priority=t.priority,
                status=t.status,
                subject=t.subject,
                description=t.description,
                created_at=t.created_at,
            )
            for t in tickets
        ]
