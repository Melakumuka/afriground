"""
Operations Engine — Maintenance management, Incident tracking, and Station Risk Evaluation.
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from fastapi import HTTPException
from pydantic import BaseModel, Field

from models.station import GroundStation, MaintenanceEvent, Incident
from models.scheduling import Schedule, Operation


# ── Enums ────────────────────────────────────────────────────────────────────

class MaintenanceType(str, Enum):
    PLANNED = "planned"
    EMERGENCY = "emergency"
    RECURRING = "recurring"

class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    RESOLVED = "resolved"
    CLOSED = "closed"


# ── Schemas ──────────────────────────────────────────────────────────────────

class MaintenanceCreateRequest(BaseModel):
    station_id: uuid.UUID
    type: MaintenanceType
    start_time: datetime
    end_time: Optional[datetime] = None
    operational_impact: str = "partial"  # full, partial, none
    description: Optional[str] = None

class MaintenanceResponse(BaseModel):
    id: uuid.UUID
    station_id: uuid.UUID
    type: str
    start_time: datetime
    end_time: Optional[datetime]
    operational_impact: str
    notified: bool
    affected_schedules: int = 0

class IncidentCreateRequest(BaseModel):
    station_id: uuid.UUID
    severity: IncidentSeverity
    description: str

class IncidentEventRequest(BaseModel):
    incident_id: uuid.UUID
    event_type: str  # status_change, note, assignment, root_cause
    content: str
    author_id: Optional[uuid.UUID] = None

class IncidentResponse(BaseModel):
    id: uuid.UUID
    station_id: uuid.UUID
    severity: str
    status: str
    description: str
    created_at: Optional[datetime] = None
    events: List[dict] = []

class StationRiskScore(BaseModel):
    station_id: uuid.UUID
    station_name: str
    overall_score: float = Field(..., ge=0, le=100, description="0=worst, 100=best")
    availability_score: float
    reliability_score: float
    weather_risk: float
    connectivity_risk: float
    maintenance_penalty: float
    recommendation: str


# ── Service ──────────────────────────────────────────────────────────────────

class OperationsEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Maintenance ──────────────────────────────────────────────────────────

    async def create_maintenance(self, req: MaintenanceCreateRequest) -> MaintenanceResponse:
        """Schedule a maintenance window and identify affected bookings."""
        station = await self.db.get(GroundStation, req.station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

        event = MaintenanceEvent(
            station_id=req.station_id,
            type=req.type.value,
            start_time=req.start_time,
            end_time=req.end_time,
            operational_impact=req.operational_impact,
            notified=False,
        )
        self.db.add(event)
        await self.db.flush()

        # Find schedules that overlap with this maintenance window
        affected_count = 0
        if req.end_time:
            stmt = select(func.count(Schedule.id)).where(
                and_(
                    Schedule.station_id == req.station_id,
                    Schedule.status.in_(["SCHEDULED", "CONFIRMED"]),
                )
            )
            result = await self.db.execute(stmt)
            affected_count = result.scalar() or 0

        # In production: trigger notification to affected customers via Celery task
        event.notified = True

        await self.db.commit()
        await self.db.refresh(event)

        return MaintenanceResponse(
            id=event.id,
            station_id=event.station_id,
            type=event.type,
            start_time=event.start_time,
            end_time=event.end_time,
            operational_impact=event.operational_impact,
            notified=event.notified,
            affected_schedules=affected_count,
        )

    async def list_maintenance(
        self, station_id: uuid.UUID, upcoming_only: bool = True
    ) -> List[MaintenanceResponse]:
        """List maintenance events for a station."""
        stmt = select(MaintenanceEvent).where(MaintenanceEvent.station_id == station_id)
        if upcoming_only:
            stmt = stmt.where(
                MaintenanceEvent.end_time == None  # noqa: E711
            ).union(
                select(MaintenanceEvent).where(
                    MaintenanceEvent.station_id == station_id,
                    MaintenanceEvent.end_time >= datetime.utcnow(),
                )
            )
        stmt = stmt.order_by(MaintenanceEvent.start_time)
        result = await self.db.execute(stmt)
        events = result.scalars().all()

        return [
            MaintenanceResponse(
                id=e.id,
                station_id=e.station_id,
                type=e.type,
                start_time=e.start_time,
                end_time=e.end_time,
                operational_impact=e.operational_impact,
                notified=e.notified,
            )
            for e in events
        ]

    # ── Incidents ────────────────────────────────────────────────────────────

    async def create_incident(self, req: IncidentCreateRequest) -> IncidentResponse:
        """Open a new incident for a ground station."""
        station = await self.db.get(GroundStation, req.station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

        incident = Incident(
            station_id=req.station_id,
            severity=req.severity.value,
            status=IncidentStatus.OPEN.value,
            description=req.description,
        )
        self.db.add(incident)
        await self.db.commit()
        await self.db.refresh(incident)

        return IncidentResponse(
            id=incident.id,
            station_id=incident.station_id,
            severity=incident.severity,
            status=incident.status,
            description=incident.description,
            created_at=incident.created_at,
        )

    async def update_incident_status(
        self, incident_id: uuid.UUID, new_status: IncidentStatus, note: str = ""
    ) -> IncidentResponse:
        """Transition an incident to a new status."""
        incident = await self.db.get(Incident, incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")

        # Validate transition
        valid_transitions = {
            "open": ["investigating"],
            "investigating": ["identified", "resolved"],
            "identified": ["resolved"],
            "resolved": ["closed", "investigating"],  # can reopen
            "closed": [],
        }
        if new_status.value not in valid_transitions.get(incident.status, []):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transition from '{incident.status}' to '{new_status.value}'",
            )

        incident.status = new_status.value
        await self.db.commit()
        await self.db.refresh(incident)

        return IncidentResponse(
            id=incident.id,
            station_id=incident.station_id,
            severity=incident.severity,
            status=incident.status,
            description=incident.description,
            created_at=incident.created_at,
        )

    async def list_incidents(
        self, station_id: Optional[uuid.UUID] = None, open_only: bool = True
    ) -> List[IncidentResponse]:
        """List incidents, optionally filtered by station and status."""
        stmt = select(Incident)
        if station_id:
            stmt = stmt.where(Incident.station_id == station_id)
        if open_only:
            stmt = stmt.where(Incident.status.in_(["open", "investigating", "identified"]))
        stmt = stmt.order_by(Incident.created_at.desc())

        result = await self.db.execute(stmt)
        incidents = result.scalars().all()

        return [
            IncidentResponse(
                id=i.id,
                station_id=i.station_id,
                severity=i.severity,
                status=i.status,
                description=i.description,
                created_at=i.created_at,
            )
            for i in incidents
        ]

    # ── Station Risk Evaluation ──────────────────────────────────────────────

    async def evaluate_station_risk(self, station_id: uuid.UUID) -> StationRiskScore:
        """
        Calculate a composite risk score for a ground station.
        Used by the scheduler to optimize pass routing across a multi-station network.

        Factors:
        - Availability: Is the station currently operational and not in maintenance?
        - Reliability: Historical pass success rate.
        - Weather risk: Based on seasonal weather data (placeholder for ML model).
        - Connectivity risk: Network uplink reliability.
        - Maintenance penalty: Upcoming maintenance windows reduce score.
        """
        station = await self.db.get(GroundStation, station_id)
        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

        # ── Availability Score (0-100) ───────────────────────────────────────
        availability = 100.0
        if station.status == "maintenance":
            availability = 20.0
        elif station.status == "offline":
            availability = 0.0

        # Check for active incidents
        stmt = select(func.count(Incident.id)).where(
            and_(
                Incident.station_id == station_id,
                Incident.status.in_(["open", "investigating"]),
            )
        )
        result = await self.db.execute(stmt)
        open_incidents = result.scalar() or 0
        if open_incidents > 0:
            availability -= min(30, open_incidents * 15)

        # ── Reliability Score (0-100) ────────────────────────────────────────
        # In production, calculate from operations table success/failure ratio
        # For now, use a placeholder based on station status
        reliability = 95.0 if station.status == "operational" else 70.0

        # ── Weather Risk (0-100, lower = more risky) ─────────────────────────
        # Placeholder — in production, integrate weather API or ML model
        # Entoto is at ~3,000m altitude, generally clear skies
        weather_risk = 85.0  # Good conditions most of the year

        # ── Connectivity Risk (0-100) ────────────────────────────────────────
        connectivity = 90.0  # Assume good network connectivity

        # ── Maintenance Penalty ──────────────────────────────────────────────
        stmt = select(func.count(MaintenanceEvent.id)).where(
            and_(
                MaintenanceEvent.station_id == station_id,
                MaintenanceEvent.start_time <= datetime.utcnow() + timedelta(days=7),
                MaintenanceEvent.end_time >= datetime.utcnow(),
            )
        )
        result = await self.db.execute(stmt)
        upcoming_maintenance = result.scalar() or 0
        maintenance_penalty = min(20, upcoming_maintenance * 10)

        # ── Composite Score ──────────────────────────────────────────────────
        overall = (
            availability * 0.30
            + reliability * 0.30
            + weather_risk * 0.15
            + connectivity * 0.15
            - maintenance_penalty
        )
        overall = max(0, min(100, round(overall, 1)))

        # Recommendation
        if overall >= 80:
            recommendation = "Preferred — high confidence for scheduling"
        elif overall >= 50:
            recommendation = "Acceptable — monitor conditions before pass"
        else:
            recommendation = "Not recommended — consider alternate station"

        return StationRiskScore(
            station_id=station_id,
            station_name=station.name,
            overall_score=overall,
            availability_score=round(max(0, availability), 1),
            reliability_score=round(reliability, 1),
            weather_risk=round(weather_risk, 1),
            connectivity_risk=round(connectivity, 1),
            maintenance_penalty=round(maintenance_penalty, 1),
            recommendation=recommendation,
        )
