"""
Contact Planning — the operational chain:
VisibilityOpportunity -> ContactOpportunity -> Reservation -> ScheduledContact -> ObservationJob.
See docs/STATE_MACHINE_SPEC.md and docs/implementation_plan.md (Phase 1.4).
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.contact import (
    VisibilityOpportunity,
    ContactOpportunity,
    Reservation,
    ScheduledContact,
)
from models.mission import (
    Spacecraft,
    MissionProfile,
    MissionRFProfile,
    MissionOperationalConstraint,
)
from models.station import GroundStation
from models.station_twin import StationCapability, StationCertification
from services.outbox import emit
from services.sgp4_engine import SGP4Engine
from services.state_machine import RESERVATION_SM, CONTACT_OPPORTUNITY_SM
from services.tenancy import TenantContext, write_audit_log
from services.network_routing import NetworkRoutingService


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ContactPlanningService:
    def __init__(self, db: AsyncSession, tenant: TenantContext):
        self.db = db
        self.tenant = tenant
        self.sgp4 = SGP4Engine()
        self.routing = NetworkRoutingService(db)

    # ── Visibility opportunities ────────────────────────────────────────────

    async def generate_visibility_opportunities(
        self,
        spacecraft_id: uuid.UUID,
        station_ids: List[uuid.UUID],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        min_elevation_deg: float = 5.0,
    ) -> List[VisibilityOpportunity]:
        spacecraft = await self.db.get(Spacecraft, spacecraft_id)
        if not spacecraft or spacecraft.org_id != self.tenant.org_id:
            raise HTTPException(status_code=404, detail="Spacecraft not found")

        start = start or _now()
        end = end or (start + timedelta(days=1))

        tles = await self._get_active_tle(spacecraft)
        if not tles:
            raise HTTPException(status_code=400, detail="No active TLE for spacecraft")

        created: List[VisibilityOpportunity] = []
        for station_id in station_ids:
            station = await self.db.get(GroundStation, station_id)
            if not station:
                raise HTTPException(status_code=404, detail=f"Station {station_id} not found")

            passes = self.sgp4.predict_passes(
                tles["line1"],
                tles["line2"],
                station.latitude,
                station.longitude,
                station.altitude_m,
                start,
                end,
                min_elevation_deg=max(min_elevation_deg, station.min_elevation_deg or 5.0),
            )

            for p in passes:
                dup = (
                    await self.db.execute(
                        select(VisibilityOpportunity.id).where(
                            and_(
                                VisibilityOpportunity.spacecraft_id == spacecraft_id,
                                VisibilityOpportunity.station_id == station.id,
                                VisibilityOpportunity.aos == p.aos,
                            )
                        )
                    )
                ).scalar_one_or_none()
                if dup:
                    continue

                vis = VisibilityOpportunity(
                    org_id=self.tenant.org_id,
                    spacecraft_id=spacecraft_id,
                    station_id=station.id,
                    aos=p.aos,
                    los=p.los,
                    max_elevation_deg=p.max_elevation,
                    duration_seconds=p.duration_seconds,
                    status="OPEN",
                )
                self.db.add(vis)
                await self.db.flush()
                emit(
                    self.db,
                    aggregate_type="visibility_opportunity",
                    aggregate_id=vis.id,
                    event_type="VISIBILITY_OPPORTUNITY.CREATED",
                    payload={"vis_id": str(vis.id), "spacecraft_id": str(spacecraft_id), "station_id": str(station.id)},
                )
                created.append(vis)

        await self.db.commit()
        for vis in created:
            await self.db.refresh(vis)
        return created

    # ── Contact opportunities ───────────────────────────────────────────────

    async def create_contact_opportunities(
        self,
        visibility_ids: List[uuid.UUID],
        mission_profile_id: uuid.UUID,
    ) -> List[ContactOpportunity]:
        profile = await self.db.get(MissionProfile, mission_profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Mission profile not found")

        rf_profile = (
            await self.db.execute(
                select(MissionRFProfile).where(
                    MissionRFProfile.mission_profile_id == mission_profile_id,
                    MissionRFProfile.is_active == True,  # noqa: E712
                )
            )
        ).scalar_one_or_none()

        created: List[ContactOpportunity] = []
        for vis_id in visibility_ids:
            vis = await self.db.get(VisibilityOpportunity, vis_id)
            if not vis or vis.org_id != self.tenant.org_id:
                raise HTTPException(status_code=404, detail=f"Visibility opportunity {vis_id} not found")
            if vis.status != "OPEN":
                raise HTTPException(status_code=409, detail=f"Visibility opportunity {vis_id} is {vis.status}")

            station = await self.db.get(GroundStation, vis.station_id)
            if station and not self._is_certified(station):
                raise HTTPException(
                    status_code=400,
                    detail=f"Station {station.code} is not certified for contacts",
                )

            # Mission operational constraints (Phase 3.2): station restrictions
            # and minimum elevation turn infeasible opportunities CLOSED.
            constraint_reason = await self._constraint_block(profile.mission_id, station, vis)

            # RF feasibility vs station capabilities
            band_ok, score = await self._score_opportunity(vis, station, rf_profile)
            if constraint_reason:
                band_ok = False
                score = 0.0

            opp = ContactOpportunity(
                org_id=self.tenant.org_id,
                visibility_opportunity_id=vis.id,
                mission_profile_id=mission_profile_id,
                rf_profile_id=rf_profile.id if rf_profile else None,
                required_band=rf_profile.band if rf_profile else None,
                min_elevation_deg=vis.max_elevation_deg,
                estimated_duration_seconds=vis.duration_seconds,
                opportunity_score=score,
                status="OPEN" if band_ok else "CLOSED",
            )
            self.db.add(opp)
            await self.db.flush()
            vis.status = "PROMOTED"
            created.append(opp)

        await self.db.commit()
        for opp in created:
            await self.db.refresh(opp)
        return created

    async def _score_opportunity(self, vis: VisibilityOpportunity, station: Optional[GroundStation], rf_profile: Optional[MissionRFProfile]) -> tuple[bool, float]:
        if not station or not rf_profile:
            return False, 0.0
        cap_row = (
            await self.db.execute(
                select(StationCapability).where(
                    StationCapability.station_id == station.id,
                    StationCapability.band == rf_profile.band,
                )
            )
        ).scalars().first()
        if cap_row is None:
            return False, 0.0

        score = vis.max_elevation_deg
        if vis.duration_seconds:
            score += vis.duration_seconds / 300.0  # bonus for longer passes
        if cap_row.gain_dbi:
            score += cap_row.gain_dbi / 10.0
        # Network routing bonus (Phase 3.2): measured quality + risk + heartbeat.
        score += await self.routing.station_bonus(station.id)
        return True, round(score, 2)

    async def _constraint_block(
        self,
        mission_id: uuid.UUID,
        station: Optional[GroundStation],
        vis: VisibilityOpportunity,
    ) -> Optional[str]:
        """Return a reason string when a mission operational constraint makes
        this opportunity infeasible, else None (Phase 3.2)."""
        result = await self.db.execute(
            select(MissionOperationalConstraint).where(
                MissionOperationalConstraint.mission_id == mission_id,
                MissionOperationalConstraint.is_active == True,  # noqa: E712
            )
        )
        constraints = result.scalars().all()
        if not constraints:
            return None

        for constraint in constraints:
            value = constraint.value or {}
            if constraint.constraint_type == "station_restriction":
                allowed = value.get("station_ids") or []
                if station and allowed and station.id not in allowed:
                    return f"station restricted by mission constraints (allowed: {len(allowed)})"
            elif constraint.constraint_type == "min_elevation":
                required = float(value.get("min_elevation_deg", 0) or 0)
                if vis.max_elevation_deg < required:
                    return f"pass elevation {vis.max_elevation_deg} below required {required}"
            elif constraint.constraint_type == "blackout_window":
                start = value.get("start")
                end = value.get("end")
                if start and end:
                    from datetime import datetime as _dt

                    try:
                        start_dt = _dt.fromisoformat(start.replace("Z", "+00:00"))
                        end_dt = _dt.fromisoformat(end.replace("Z", "+00:00"))
                    except ValueError:
                        continue
                    if start_dt <= vis.aos <= end_dt:
                        return "inside mission blackout window"
        return None

    # ── Reservations ────────────────────────────────────────────────────────

    async def create_reservation(
        self,
        contact_opportunity_id: uuid.UUID,
        customer_org_id: uuid.UUID,
        spacecraft_id: uuid.UUID,
        mission_id: Optional[uuid.UUID] = None,
        expires_at: Optional[datetime] = None,
    ) -> Reservation:
        opp = await self.db.get(ContactOpportunity, contact_opportunity_id)
        if not opp or opp.org_id != self.tenant.org_id:
            raise HTTPException(status_code=404, detail="Contact opportunity not found")
        if opp.status != "OPEN":
            raise HTTPException(status_code=409, detail=f"Contact opportunity is {opp.status}")

        reservation = Reservation(
            org_id=self.tenant.org_id,
            contact_opportunity_id=contact_opportunity_id,
            customer_org_id=customer_org_id,
            spacecraft_id=spacecraft_id,
            mission_id=mission_id,
            status="REQUESTED",
            expires_at=expires_at or (_now() + timedelta(hours=24)),
        )
        self.db.add(reservation)
        await self.db.flush()
        opp.status = "RESERVED"

        emit(
            self.db,
            aggregate_type="reservation",
            aggregate_id=reservation.id,
            event_type="RESERVATION.REQUESTED",
            payload={
                "reservation_id": str(reservation.id),
                "opportunity_id": str(contact_opportunity_id),
                "customer_org_id": str(customer_org_id),
            },
        )
        await self.db.commit()
        await self.db.refresh(reservation)
        return reservation

    async def confirm_reservation(self, reservation_id: uuid.UUID) -> Reservation:
        reservation = await self._get_reservation(reservation_id)
        RESERVATION_SM.validate(reservation.status, "CONFIRMED")
        reservation.status = "CONFIRMED"
        reservation.confirmed_at = _now()
        await self.db.commit()
        await self.db.refresh(reservation)
        return reservation

    # ── Scheduled contacts ──────────────────────────────────────────────────

    async def schedule_contact(
        self,
        reservation_id: uuid.UUID,
        scheduled_start: Optional[datetime] = None,
        scheduled_end: Optional[datetime] = None,
    ) -> ScheduledContact:
        reservation = await self._get_reservation(reservation_id)
        if reservation.status != "CONFIRMED":
            raise HTTPException(status_code=400, detail="Reservation must be CONFIRMED to schedule")

        opp = await self.db.get(ContactOpportunity, reservation.contact_opportunity_id)
        vis = await self.db.get(VisibilityOpportunity, opp.visibility_opportunity_id)

        contact = ScheduledContact(
            org_id=self.tenant.org_id,
            reservation_id=reservation.id,
            contact_opportunity_id=opp.id,
            station_id=vis.station_id,
            spacecraft_id=reservation.spacecraft_id,
            scheduled_start=scheduled_start or vis.aos,
            scheduled_end=scheduled_end or vis.los,
            status="CONFIRMED",
        )
        self.db.add(contact)
        await self.db.flush()
        opp.status = "CLOSED"

        emit(
            self.db,
            aggregate_type="scheduled_contact",
            aggregate_id=contact.id,
            event_type="SCHEDULED_CONTACT.CREATED",
            payload={"contact_id": str(contact.id), "reservation_id": str(reservation_id)},
        )
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    # ── Full chain helper ───────────────────────────────────────────────────

    async def plan_contact(
        self,
        spacecraft_id: uuid.UUID,
        mission_profile_id: uuid.UUID,
        customer_org_id: uuid.UUID,
        station_ids: List[uuid.UUID],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> dict:
        """Generate opportunities and (best) reservation for a mission profile."""
        visibilities = await self.generate_visibility_opportunities(spacecraft_id, station_ids, start, end)
        if not visibilities:
            raise HTTPException(status_code=404, detail="No visibility opportunities in window")

        vis_ids = [v.id for v in visibilities]
        opportunities = await self.create_contact_opportunities(vis_ids, mission_profile_id)
        open_opps = [o for o in opportunities if o.status == "OPEN"]
        if not open_opps:
            raise HTTPException(status_code=400, detail="No feasible contact opportunities")

        best = max(open_opps, key=lambda o: o.opportunity_score or 0)
        reservation = await self.create_reservation(
            best.id, customer_org_id, spacecraft_id=spacecraft_id
        )
        return {
            "visibility_opportunities": len(visibilities),
            "contact_opportunities": len(opportunities),
            "best_opportunity_id": str(best.id),
            "opportunity_score": best.opportunity_score,
            "reservation_id": str(reservation.id),
        }

    # ── Helpers ─────────────────────────────────────────────────────────────

    async def _get_reservation(self, reservation_id: uuid.UUID) -> Reservation:
        reservation = await self.db.get(Reservation, reservation_id)
        if not reservation or reservation.org_id != self.tenant.org_id:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return reservation

    async def _get_active_tle(self, spacecraft: Spacecraft) -> Optional[dict]:
        from models.spacecraft import TLESet

        if spacecraft.satellite_id:
            stmt = (
                select(TLESet)
                .where(TLESet.satellite_id == spacecraft.satellite_id, TLESet.is_active == True)  # noqa: E712
                .order_by(TLESet.epoch.desc())
            )
            tle = (await self.db.execute(stmt)).scalars().first()
            if tle:
                return {"line1": tle.line1, "line2": tle.line2}
        return None

    def _is_certified(self, station: GroundStation) -> bool:
        return station.certification_state == "CERTIFIED"