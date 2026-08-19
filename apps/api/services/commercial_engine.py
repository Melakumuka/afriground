"""
Commercial Engine — Manages Quotes, Orders, Contracts, Billing, and Recurring Missions.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from models.core import Quote, Contract, Organization
from models.scheduling import Booking, RecurringMission, PassPrediction, Schedule
from models.spacecraft import Satellite, TLESet
from models.contact import ObservationJob, ScheduledContact
from models.station import GroundStation
from sqlalchemy import select, update, func, or_


# ── Pydantic Schemas ─────────────────────────────────────────────────────────

from pydantic import BaseModel, Field

class QuoteCreateRequest(BaseModel):
    org_id: uuid.UUID
    booking_ids: List[uuid.UUID]
    notes: Optional[str] = None

class QuoteResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    total_amount: float
    status: str
    line_items: List[dict]

class ContractCreateRequest(BaseModel):
    org_id: uuid.UUID
    start_date: datetime
    end_date: datetime
    reserved_capacity_minutes: int
    sla_availability_target: float = 99.5
    pricing_tier: Optional[str] = "standard"

class ContractResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    start_date: datetime
    end_date: datetime
    reserved_capacity_minutes: int
    sla_availability_target: float
    status: str
    used_minutes: int = 0
    remaining_minutes: int = 0

class RecurringMissionRequest(BaseModel):
    org_id: uuid.UUID
    satellite_id: uuid.UUID
    station_id: Optional[uuid.UUID] = None
    passes_per_day: int = 1
    start_date: datetime
    end_date: datetime

class InvoiceItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float

class InvoiceResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    period_start: datetime
    period_end: datetime
    items: List[InvoiceItem]
    subtotal: float
    tax: float
    total: float
    status: str


# ── Pricing Configuration ───────────────────────────────────────────────────

PRICING = {
    "standard": {
        "per_minute_usd": 15.0,
        "setup_fee_usd": 500.0,
    },
    "premium": {
        "per_minute_usd": 12.0,
        "setup_fee_usd": 0.0,
    },
    "enterprise": {
        "per_minute_usd": 8.0,
        "setup_fee_usd": 0.0,
    },
}


# ── Service ──────────────────────────────────────────────────────────────────

class CommercialEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Quotes ───────────────────────────────────────────────────────────────

    async def create_quote(self, req: QuoteCreateRequest) -> QuoteResponse:
        """
        Generate a price quote for one or more bookings.
        Calculates cost based on predicted pass durations and the org's pricing tier.
        """
        # Determine pricing tier from active contract, default to standard
        contract = await self._get_active_contract(req.org_id)
        tier = "standard"
        if contract and contract.status == "active":
            # Enterprise contracts get enterprise pricing
            tier = "enterprise"

        pricing = PRICING[tier]
        line_items = []
        total = 0.0

        for booking_id in req.booking_ids:
            booking = await self.db.get(Booking, booking_id)
            if not booking:
                raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")

            # Get the associated schedule and pass prediction for duration
            stmt = select(Schedule).where(Schedule.booking_id == booking_id)
            result = await self.db.execute(stmt)
            schedule = result.scalar_one_or_none()

            duration_minutes = 10  # default fallback
            if schedule:
                pred = await self.db.get(PassPrediction, schedule.pass_prediction_id)
                if pred:
                    duration_minutes = max(1, pred.duration_seconds // 60)

            item_cost = duration_minutes * pricing["per_minute_usd"]
            line_items.append({
                "booking_id": str(booking_id),
                "duration_minutes": duration_minutes,
                "rate_per_minute": pricing["per_minute_usd"],
                "subtotal": item_cost,
            })
            total += item_cost

        # Add setup fee if applicable
        if pricing["setup_fee_usd"] > 0:
            line_items.append({
                "description": "One-time setup fee",
                "subtotal": pricing["setup_fee_usd"],
            })
            total += pricing["setup_fee_usd"]

        quote = Quote(
            org_id=req.org_id,
            total_amount=round(total, 2),
            status="draft",
        )
        self.db.add(quote)
        await self.db.flush()

        # Transition bookings to QUOTED status
        for booking_id in req.booking_ids:
            await self.db.execute(
                update(Booking).where(Booking.id == booking_id).values(
                    status="QUOTED", quote_id=quote.id
                )
            )

        await self.db.commit()
        await self.db.refresh(quote)

        return QuoteResponse(
            id=quote.id,
            org_id=quote.org_id,
            total_amount=quote.total_amount,
            status=quote.status,
            line_items=line_items,
        )

    async def accept_quote(self, quote_id: uuid.UUID) -> QuoteResponse:
        """Customer accepts a quote — transitions bookings to RESERVED."""
        quote = await self.db.get(Quote, quote_id)
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")
        if quote.status != "draft" and quote.status != "sent":
            raise HTTPException(status_code=400, detail=f"Quote in status '{quote.status}' cannot be accepted")

        quote.status = "accepted"

        # Transition all bookings tied to this quote to RESERVED
        stmt = select(Booking).where(Booking.quote_id == quote_id)
        result = await self.db.execute(stmt)
        bookings = result.scalars().all()
        for booking in bookings:
            booking.status = "RESERVED"

        await self.db.commit()
        await self.db.refresh(quote)

        return QuoteResponse(
            id=quote.id,
            org_id=quote.org_id,
            total_amount=quote.total_amount,
            status=quote.status,
            line_items=[],
        )

    # ── Contracts ────────────────────────────────────────────────────────────

    async def create_contract(self, req: ContractCreateRequest) -> ContractResponse:
        """Create a reserved-capacity enterprise contract."""
        contract = Contract(
            org_id=req.org_id,
            start_date=req.start_date,
            end_date=req.end_date,
            reserved_capacity_minutes=req.reserved_capacity_minutes,
            sla_availability_target=req.sla_availability_target,
            status="active",
        )
        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract)

        return ContractResponse(
            id=contract.id,
            org_id=contract.org_id,
            start_date=contract.start_date,
            end_date=contract.end_date,
            reserved_capacity_minutes=contract.reserved_capacity_minutes,
            sla_availability_target=contract.sla_availability_target,
            status=contract.status,
            used_minutes=0,
            remaining_minutes=contract.reserved_capacity_minutes,
        )

    async def get_contract_usage(self, contract_id: uuid.UUID) -> ContractResponse:
        """Get contract details including usage against reserved capacity.

        Usage is aggregated from completed observation jobs under the org whose
        completion falls inside the contract window (minutes on air).
        """
        contract = await self.db.get(Contract, contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")

        used_minutes = await self._aggregate_used_minutes(contract)

        return ContractResponse(
            id=contract.id,
            org_id=contract.org_id,
            start_date=contract.start_date,
            end_date=contract.end_date,
            reserved_capacity_minutes=contract.reserved_capacity_minutes,
            sla_availability_target=contract.sla_availability_target,
            status=contract.status,
            used_minutes=used_minutes,
            remaining_minutes=max(contract.reserved_capacity_minutes - used_minutes, 0),
        )

    async def _aggregate_used_minutes(self, contract: Contract) -> int:
        """Sum completed contact durations (minutes) for the org in the contract window."""
        on_air_seconds = (
            func.extract(
                "epoch",
                ScheduledContact.scheduled_end - ScheduledContact.scheduled_start,
            )
        )
        stmt = (
            select(func.coalesce(func.sum(on_air_seconds), 0.0))
            .select_from(ObservationJob)
            .join(ScheduledContact, ScheduledContact.id == ObservationJob.scheduled_contact_id)
            .where(
                ObservationJob.org_id == contract.org_id,
                ObservationJob.status == "COMPLETED",
                ObservationJob.completed_at.isnot(None),
            )
        )
        if contract.start_date:
            stmt = stmt.where(ObservationJob.completed_at >= contract.start_date)
        if contract.end_date:
            stmt = stmt.where(ObservationJob.completed_at <= contract.end_date)

        total_seconds = (await self.db.execute(stmt)).scalar() or 0.0
        return int(total_seconds // 60)

    # ── Recurring Missions ───────────────────────────────────────────────────

    async def create_recurring_mission(self, req: RecurringMissionRequest) -> dict:
        """
        Create a recurring mission that auto-generates bookings for X passes/day.
        """
        mission = RecurringMission(
            org_id=req.org_id,
            satellite_id=req.satellite_id,
            station_id=req.station_id,
            passes_per_day=req.passes_per_day,
            start_date=req.start_date,
            end_date=req.end_date,
            status="active",
        )
        self.db.add(mission)
        await self.db.commit()
        await self.db.refresh(mission)

        # In production, a Celery task would periodically scan active recurring missions,
        # run SGP4 predictions, and auto-create bookings for the next N days.

        return {
            "id": str(mission.id),
            "satellite_id": str(mission.satellite_id),
            "passes_per_day": mission.passes_per_day,
            "start_date": str(mission.start_date),
            "end_date": str(mission.end_date),
            "status": mission.status,
            "message": "Recurring mission created. Bookings will be auto-generated.",
        }

    # ── Helpers ──────────────────────────────────────────────────────────────

    async def _get_active_contract(self, org_id: uuid.UUID) -> Optional[Contract]:
        stmt = select(Contract).where(
            Contract.org_id == org_id,
            Contract.status == "active",
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


# ── Recurring Mission Sweeper (Phase 3.0) ────────────────────────────────────

class RecurringMissionSweeper:
    """Auto-generates bookings for active recurring missions from TLE pass
    predictions. Runs on a Celery beat schedule (and manually via API)."""

    SWEEP_WINDOW_HOURS = 24

    def __init__(self, db: AsyncSession):
        self.db = db
        from services.sgp4_engine import SGP4Engine

        self.sgp4 = SGP4Engine()

    async def sweep(self, org_id: Optional[uuid.UUID] = None) -> int:
        """Create bookings for every due recurring mission. Returns count created."""
        now = datetime.now(timezone.utc)
        stmt = select(RecurringMission).where(
            RecurringMission.status == "active",
            RecurringMission.start_date <= now,
            or_(
                RecurringMission.end_date.is_(None),
                RecurringMission.end_date >= now,
            ),
        )
        if org_id:
            stmt = stmt.where(RecurringMission.org_id == org_id)
        result = await self.db.execute(stmt)
        missions = result.scalars().all()

        created = 0
        for mission in missions:
            created += await self._sweep_mission(mission, now)

        if created:
            await self.db.commit()
        return created

    async def _sweep_mission(self, mission: RecurringMission, now: datetime) -> int:
        tle = (
            await self.db.execute(
                select(TLESet).where(
                    TLESet.satellite_id == mission.satellite_id,
                    TLESet.is_active == True,  # noqa: E712
                )
            )
        ).scalars().first()
        if not tle:
            return 0

        station_ids = [mission.station_id] if mission.station_id else None
        if station_ids is None:
            rows = await self.db.execute(
                select(GroundStation.id).where(GroundStation.status == "operational")
            )
            station_ids = rows.scalars().all()

        window_end = now + timedelta(hours=self.SWEEP_WINDOW_HOURS)

        candidates = []
        for station_id in station_ids:
            station = await self.db.get(GroundStation, station_id)
            if not station:
                continue
            passes = self.sgp4.predict_passes(
                tle.line1,
                tle.line2,
                station.latitude,
                station.longitude,
                station.altitude_m,
                now,
                window_end,
                min_elevation_deg=max(station.min_elevation_deg or 5.0, 5.0),
            )
            for p in passes:
                candidates.append((station, p))

        if not candidates:
            return 0

        # Dedupe against passes already booked for this recurring mission.
        booked_pairs = set(
            (
                await self.db.execute(
                    select(PassPrediction.station_id, PassPrediction.aos)
                    .join(Schedule, Schedule.pass_prediction_id == PassPrediction.id)
                    .join(Booking, Booking.id == Schedule.booking_id)
                    .where(Booking.recurring_mission_id == mission.id)
                )
            ).all()
        )

        # Pick the best passes_per_day opportunities (by elevation then time).
        candidates.sort(key=lambda c: (-c[1].max_elevation, c[1].aos))
        created = 0
        for station, p in candidates:
            if created >= mission.passes_per_day:
                break
            if (station.id, p.aos) in booked_pairs:
                continue

            pred = PassPrediction(
                satellite_id=mission.satellite_id,
                station_id=station.id,
                aos=p.aos,
                los=p.los,
                max_elevation=p.max_elevation,
                duration_seconds=p.duration_seconds,
            )
            self.db.add(pred)
            await self.db.flush()

            booking = Booking(
                org_id=mission.org_id,
                satellite_id=mission.satellite_id,
                status="REQUESTED",
                recurring_mission_id=mission.id,
            )
            self.db.add(booking)
            await self.db.flush()

            self.db.add(
                Schedule(
                    booking_id=booking.id,
                    pass_prediction_id=pred.id,
                    station_id=station.id,
                    status="SCHEDULED",
                )
            )
            created += 1
        return created
