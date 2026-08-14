"""
Network Routing Engine — Multi-station orchestration and Hardware failover logic.
"""
import uuid
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from models.station import GroundStation
from models.scheduling import PassPrediction, Booking, Schedule
from services.operations_engine import OperationsEngine
from services.matcher import CompatibilityEngine

logger = logging.getLogger(__name__)


class RoutingEngine:
    """
    Handles scheduling across a multi-station network.
    Selects the optimal ground station based on risk scores, hardware availability,
    and automatic failover rules.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ops_engine = OperationsEngine(db)
        self.matcher = CompatibilityEngine(db)

    async def find_optimal_station(
        self, satellite_id: uuid.UUID, target_time: datetime
    ) -> Optional[uuid.UUID]:
        """
        Evaluate all ground stations in the network and return the ID of the optimal station
        for the given satellite at the given time.
        """
        # 1. Fetch all operational ground stations
        stmt = select(GroundStation).where(GroundStation.status == "operational")
        result = await self.db.execute(stmt)
        stations = result.scalars().all()

        if not stations:
            logger.warning("No operational ground stations available in the network.")
            return None

        candidates = []

        for station in stations:
            # 2. Check strict hardware RF compatibility
            is_compatible = await self.matcher.evaluate_compatibility(satellite_id, station.id)
            if not is_compatible:
                continue

            # 3. Check schedule conflicts (ensure antenna is not already booked at target_time)
            # In a real app, this would check a precise time window overlap
            conflict_stmt = select(Schedule).where(
                and_(
                    Schedule.station_id == station.id,
                    Schedule.status.in_(["SCHEDULED", "CONFIRMED"]),
                    # Placeholder for time overlap logic
                )
            )
            conflicts = (await self.db.execute(conflict_stmt)).scalars().all()
            if conflicts:
                continue

            # 4. Evaluate composite risk score
            risk_profile = await self.ops_engine.evaluate_station_risk(station.id)
            
            candidates.append({
                "station_id": station.id,
                "score": risk_profile.overall_score
            })

        if not candidates:
            logger.warning(f"No compatible, available stations for satellite {satellite_id}")
            return None

        # 5. Sort by best score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Return the best candidate
        best_station_id = candidates[0]["station_id"]
        logger.info(f"Selected optimal station {best_station_id} with score {candidates[0]['score']}")
        return best_station_id

    async def trigger_failover(self, schedule_id: uuid.UUID) -> bool:
        """
        Called when a scheduled pass is about to fail due to sudden hardware degradation.
        Attempts to transparently migrate the booking to an alternate station.
        """
        schedule = await self.db.get(Schedule, schedule_id)
        if not schedule:
            return False

        pred = await self.db.get(PassPrediction, schedule.pass_prediction_id)
        if not pred:
            return False

        logger.info(f"Triggering automatic failover for schedule {schedule_id}")

        # Try to find a backup station
        backup_station_id = await self.find_optimal_station(pred.satellite_id, pred.aos_time)

        if not backup_station_id:
            logger.error(f"Failover failed: No alternate stations available for {schedule_id}")
            schedule.status = "FAILED"
            await self.db.commit()
            return False

        # Execute failover
        schedule.station_id = backup_station_id
        schedule.notes = (schedule.notes or "") + f" [Auto-Failover to station {backup_station_id}]"
        
        await self.db.commit()
        logger.info(f"Successfully failed over schedule {schedule_id} to station {backup_station_id}")
        return True
