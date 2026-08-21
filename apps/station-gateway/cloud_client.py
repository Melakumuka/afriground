import httpx
from config import settings

class CloudClient:
    def __init__(self):
        self.base_url = settings.cloud_api_url
        self.station_id = settings.station_id
        self.agent_id = settings.agent_id
        self.api_key = settings.cloud_api_key
        
        self.client = httpx.AsyncClient(
            base_url=f"{self.base_url}/api/v1/edge",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    async def get_assigned_jobs(self):
        resp = await self.client.get(f"/stations/{self.station_id}/jobs/assigned")
        resp.raise_for_status()
        return resp.json()

    async def get_profile(self, profile_id: str):
        resp = await self.client.get(f"/profiles/{profile_id}")
        resp.raise_for_status()
        return resp.json()

    async def acknowledge_job(self, job_id: str):
        resp = await self.client.post(f"/jobs/{job_id}/acknowledge", json={"agent_id": self.agent_id})
        resp.raise_for_status()
        return resp.json()

    async def submit_readiness(self, job_id: str, status: str, checklist_results: dict):
        resp = await self.client.post(f"/jobs/{job_id}/readiness", json={"status": status, "checklist_results": checklist_results})
        resp.raise_for_status()
        return resp.json()

    async def submit_receipt(self, payload: dict):
        resp = await self.client.post("/receipts", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def get_station_profiles(self):
        resp = await self.client.get(f"/stations/{self.station_id}/profiles")
        resp.raise_for_status()
        return resp.json()

    async def report_heartbeat(self, metrics: dict):
        payload = {
            "agent_version": settings.agent_version,
            "metrics": metrics
        }
        resp = await self.client.post(f"/stations/{self.station_id}/agents/{self.agent_id}/heartbeat", json=payload)
        resp.raise_for_status()
        return resp.json()
