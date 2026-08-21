import asyncio
import logging
from cloud_client import CloudClient
from local_db import AsyncSessionLocal, CachedJob, CachedProfile
from adapters import get_adapter
from config import settings

logger = logging.getLogger(__name__)

class BackgroundWorker:
    def __init__(self):
        self.client = CloudClient()
        self.adapter = get_adapter(settings.adapter_type)
        self.sync_interval = 10  # seconds
        self.heartbeat_interval = 5  # seconds
        self._running = False
        self.sync_task = None
        self.heartbeat_task = None

    async def start(self):
        self._running = True
        self.sync_task = asyncio.create_task(self._sync_loop())
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("Background workers started.")

    async def stop(self):
        self._running = False
        if self.sync_task:
            self.sync_task.cancel()
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        logger.info("Background workers stopped.")

    async def _sync_loop(self):
        while self._running:
            try:
                await self._sync_profiles()
                await self._sync_jobs()
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
            await asyncio.sleep(self.sync_interval)

    async def _heartbeat_loop(self):
        while self._running:
            try:
                health = await self.adapter.get_station_health()
                await self.client.report_heartbeat(metrics=health)
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
            await asyncio.sleep(self.heartbeat_interval)

    async def _sync_profiles(self):
        profiles = await self.client.get_station_profiles()
        async with AsyncSessionLocal() as session:
            for p in profiles:
                existing = await session.get(CachedProfile, p["id"])
                if not existing:
                    # fetch full profile detail
                    detail = await self.client.get_profile(p["id"])
                    import json
                    new_prof = CachedProfile(
                        id=detail["id"],
                        name=detail["name"],
                        satellite_id=detail.get("satellite_id"),
                        operation_mode=detail.get("operation_mode"),
                        mcs_profile_payload=json.dumps(detail.get("mcs_profile_payload", {})),
                        hdr_config_payload=json.dumps(detail.get("hdr_config_payload", {})),
                        acu_config_payload=json.dumps(detail.get("acu_config_payload", {}))
                    )
                    session.add(new_prof)
                else:
                    pass
            await session.commit()

    async def _sync_jobs(self):
        jobs = await self.client.get_assigned_jobs()
        async with AsyncSessionLocal() as session:
            for j in jobs:
                existing = await session.get(CachedJob, j["id"])
                if not existing:
                    new_job = CachedJob(
                        id=j["id"],
                        status=j["status"],
                        readiness_status=j["readiness_status"],
                        mission_profile_id=j["mission_profile_id"],
                        station_operation_profile_id=j.get("station_operation_profile_id"),
                        priority=j.get("priority", 5),
                        tx_requested=1 if j.get("tx_requested") else 0
                    )
                    session.add(new_job)
                    await session.commit()
                    
                    if j["status"] in ("DISPATCHED", "QUEUED"):
                        try:
                            await self.client.acknowledge_job(j["id"])
                            new_job.status = "ACKNOWLEDGED"
                            session.add(new_job)
                            await session.commit()
                        except Exception as e:
                            logger.error(f"Failed to acknowledge job {j['id']}: {e}")
                else:
                    if existing.status != j["status"]:
                        existing.status = j["status"]
                        session.add(existing)
            await session.commit()
