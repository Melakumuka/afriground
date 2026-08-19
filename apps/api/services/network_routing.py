"""
Network Routing Service (Phase 3.2) — computes a composite routing score per
station by blending operational risk (OperationsEngine), measured quality
(StationQualityScore), certification state, and edge-agent heartbeat freshness.

Contact planning folds this score into opportunity scoring so `plan_contact`
naturally prefers the most reliable station across the network, and network
operations get a live station ranking.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models.station import GroundStation
from models.station_twin import (
    StationCertification,
    StationHeartbeat,
    StationQualityScore,
)
from services.operations_engine import OperationsEngine


def _now() -> datetime:
    return datetime.now(timezone.utc)


class NetworkRoutingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ops = OperationsEngine(db)
        self._bonus_cache: dict[uuid.UUID, float] = {}

    async def score_station(self, station_id: uuid.UUID) -> dict:
        """Composite routing score (0-100) for one station, with contributing factors."""
        station = await self.db.get(GroundStation, station_id)
        if not station:
            raise ValueError(f"Station {station_id} not found")

        risk = await self.ops.evaluate_station_risk(station_id)
        risk_score = risk.overall_score

        quality = await self._latest_quality(station_id)
        quality_score = quality.score if quality else 0.0

        certified = await self._is_certified(station_id)
        heartbeat_fresh = await self._heartbeat_fresh(station_id)

        composite = (
            risk_score * 0.60
            + (quality_score if quality else 50.0) * 0.30
        )
        if certified:
            composite += 5.0
        else:
            composite -= 15.0
        if heartbeat_fresh:
            composite += 5.0
        else:
            composite -= 10.0

        composite = round(max(0.0, min(100.0, composite)), 1)

        reasons = []
        if certified:
            reasons.append("certified")
        else:
            reasons.append("not-certified")
        reasons.append("heartbeat-fresh" if heartbeat_fresh else "heartbeat-stale")
        if quality and quality_score >= 80:
            reasons.append("high-quality")
        if risk_score >= 80:
            reasons.append("low-risk")

        return {
            "station_id": station_id,
            "station_name": station.name,
            "station_code": station.code,
            "composite_score": composite,
            "risk_score": risk_score,
            "quality_score": round(quality_score, 1) if quality else None,
            "certified": certified,
            "heartbeat_fresh": heartbeat_fresh,
            "reasons": reasons,
        }

    async def rank_network(self) -> List[dict]:
        stations = (
            await self.db.execute(select(GroundStation))
        ).scalars().all()
        ranked = [await self.score_station(s.id) for s in stations]
        ranked.sort(key=lambda r: r["composite_score"], reverse=True)
        return ranked

    async def station_bonus(self, station_id: uuid.UUID) -> float:
        """Normalized 0..10 contribution for opportunity scoring (cached)."""
        if station_id in self._bonus_cache:
            return self._bonus_cache[station_id]
        try:
            result = await self.score_station(station_id)
        except ValueError:
            return 0.0
        bonus = round(result["composite_score"] / 10.0, 2)
        self._bonus_cache[station_id] = bonus
        return bonus

    async def _latest_quality(self, station_id: uuid.UUID) -> Optional[StationQualityScore]:
        return (
            await self.db.execute(
                select(StationQualityScore)
                .where(StationQualityScore.station_id == station_id)
                .order_by(StationQualityScore.calculated_at.desc())
                .limit(1)
            )
        ).scalars().first()

    async def _is_certified(self, station_id: uuid.UUID) -> bool:
        cert = (
            await self.db.execute(
                select(StationCertification)
                .where(
                    StationCertification.station_id == station_id,
                    StationCertification.cert_type == "operational",
                )
                .order_by(StationCertification.created_at.desc())
                .limit(1)
            )
        ).scalars().first()
        return bool(cert and cert.current_state == "CERTIFIED")

    async def _heartbeat_fresh(self, station_id: uuid.UUID) -> bool:
        hb = (
            await self.db.execute(
                select(StationHeartbeat)
                .where(StationHeartbeat.station_id == station_id)
                .order_by(StationHeartbeat.received_at.desc())
                .limit(1)
            )
        ).scalars().first()
        if not hb or not hb.received_at:
            return False
        age = (_now() - hb.received_at).total_seconds()
        return age <= settings.heartbeat_threshold_s