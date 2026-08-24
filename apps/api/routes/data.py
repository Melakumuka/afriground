"""
API Routes — Data Catalog & Delivery Engine
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import AsyncSessionLocal
from services.data_engine import (
    DataEngine,
    DatasetResponse,
    DeliveryDestinationRequest,
    DeliveryDestinationResponse,
    DeliveryJobResponse,
)

router = APIRouter(prefix="/api/v1/data", tags=["Data Engine"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ── Datasets ─────────────────────────────────────────────────────────────────

@router.get("/datasets", response_model=List[DatasetResponse])
async def list_datasets(
    product_type: Optional[str] = Query(None),
    max_cloud_cover: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = DataEngine(db)
    return await engine.list_datasets(product_type, max_cloud_cover)


# ── Delivery Destinations ────────────────────────────────────────────────────

@router.get("/destinations", response_model=List[DeliveryDestinationResponse])
async def list_destinations(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = DataEngine(db)
    org_id = uuid.UUID(user.get("org_id", "00000000-0000-0000-0000-000000000000"))
    return await engine.list_destinations(org_id)

@router.post("/destinations", response_model=DeliveryDestinationResponse)
async def add_destination(
    req: DeliveryDestinationRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = DataEngine(db)
    return await engine.add_destination(req)


# ── Delivery Jobs ────────────────────────────────────────────────────────────

@router.post("/delivery/{dataset_id}/to/{destination_id}", response_model=DeliveryJobResponse)
async def trigger_delivery(
    dataset_id: uuid.UUID,
    destination_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = DataEngine(db)
    return await engine.trigger_delivery(dataset_id, destination_id)
