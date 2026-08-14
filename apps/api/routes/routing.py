"""
API Routes — Multi-station Routing & Failover
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from auth import get_current_user
from database import AsyncSessionLocal
from services.routing_engine import RoutingEngine

router = APIRouter(prefix="/api/v1/routing", tags=["Routing Engine"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


class FailoverResponse(BaseModel):
    schedule_id: uuid.UUID
    success: bool
    message: str


@router.post("/failover/{schedule_id}", response_model=FailoverResponse)
async def trigger_auto_failover(
    schedule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Manually trigger an automatic failover for a scheduled pass.
    The routing engine will attempt to find a backup station and migrate the schedule.
    """
    engine = RoutingEngine(db)
    success = await engine.trigger_failover(schedule_id)
    
    if success:
        return FailoverResponse(
            schedule_id=schedule_id,
            success=True,
            message="Schedule successfully migrated to a backup station."
        )
    else:
        raise HTTPException(
            status_code=400, 
            detail="Failover unsuccessful. No alternate stations are compatible or available."
        )
