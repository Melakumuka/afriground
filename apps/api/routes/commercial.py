"""
API Routes — Commercial Engine (Quotes, Contracts, Recurring Missions)
"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import AsyncSessionLocal
from services.commercial_engine import (
    CommercialEngine,
    QuoteCreateRequest,
    QuoteResponse,
    ContractCreateRequest,
    ContractResponse,
    RecurringMissionRequest,
)

router = APIRouter(prefix="/api/v1/commercial", tags=["Commercial"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ── Quotes ───────────────────────────────────────────────────────────────────

@router.post("/quotes", response_model=QuoteResponse)
async def create_quote(
    req: QuoteCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = CommercialEngine(db)
    return await engine.create_quote(req)


@router.post("/quotes/{quote_id}/accept", response_model=QuoteResponse)
async def accept_quote(
    quote_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = CommercialEngine(db)
    return await engine.accept_quote(quote_id)


# ── Contracts ────────────────────────────────────────────────────────────────

@router.post("/contracts", response_model=ContractResponse)
async def create_contract(
    req: ContractCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = CommercialEngine(db)
    return await engine.create_contract(req)


@router.get("/contracts/{contract_id}", response_model=ContractResponse)
async def get_contract_usage(
    contract_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = CommercialEngine(db)
    return await engine.get_contract_usage(contract_id)


# ── Recurring Missions ──────────────────────────────────────────────────────

@router.post("/recurring-missions")
async def create_recurring_mission(
    req: RecurringMissionRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = CommercialEngine(db)
    return await engine.create_recurring_mission(req)
