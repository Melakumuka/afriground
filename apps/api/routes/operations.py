"""
API Routes — Operations Engine (Maintenance, Incidents, Station Risk)
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import AsyncSessionLocal
from services.operations_engine import (
    OperationsEngine,
    MaintenanceCreateRequest,
    MaintenanceResponse,
    IncidentCreateRequest,
    IncidentResponse,
    IncidentStatus,
    StationRiskScore,
)

router = APIRouter(prefix="/api/v1/operations", tags=["Operations"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ── Maintenance ──────────────────────────────────────────────────────────────

@router.post("/maintenance", response_model=MaintenanceResponse)
async def create_maintenance(
    req: MaintenanceCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = OperationsEngine(db)
    return await engine.create_maintenance(req)


@router.get("/maintenance/{station_id}", response_model=list[MaintenanceResponse])
async def list_maintenance(
    station_id: uuid.UUID,
    upcoming_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = OperationsEngine(db)
    return await engine.list_maintenance(station_id, upcoming_only)


# ── Incidents ────────────────────────────────────────────────────────────────

@router.post("/incidents", response_model=IncidentResponse)
async def create_incident(
    req: IncidentCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = OperationsEngine(db)
    return await engine.create_incident(req)


@router.patch("/incidents/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: uuid.UUID,
    new_status: IncidentStatus,
    note: str = "",
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = OperationsEngine(db)
    return await engine.update_incident_status(incident_id, new_status, note)


@router.get("/incidents", response_model=list[IncidentResponse])
async def list_incidents(
    station_id: Optional[uuid.UUID] = Query(None),
    open_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = OperationsEngine(db)
    return await engine.list_incidents(station_id, open_only)


# ── Station Risk ─────────────────────────────────────────────────────────────

@router.get("/stations/{station_id}/risk", response_model=StationRiskScore)
async def evaluate_station_risk(
    station_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    engine = OperationsEngine(db)
    return await engine.evaluate_station_risk(station_id)
