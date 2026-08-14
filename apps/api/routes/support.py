"""
API Routes — Support Ticketing Engine
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import AsyncSessionLocal
from services.support_engine import (
    SupportEngine,
    TicketCreateRequest,
    TicketResponse,
)

router = APIRouter(prefix="/api/v1/support", tags=["Support Engine"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/tickets", response_model=TicketResponse)
async def create_ticket(
    req: TicketCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = SupportEngine(db)
    # Extract reporter ID from JWT (assuming uuid stored in 'sub' claim)
    reporter_id = uuid.UUID(user["sub"])
    return await engine.create_ticket(req, reporter_id)


@router.get("/tickets", response_model=List[TicketResponse])
async def list_tickets(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = SupportEngine(db)
    return await engine.list_tickets(org_id)
