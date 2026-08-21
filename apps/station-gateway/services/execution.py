import datetime
from adapters import get_adapter
from cloud_client import CloudClient
from local_db import CachedJob
from config import settings

class ExecutionService:
    def __init__(self):
        self.adapter = get_adapter(settings.adapter_type)
        self.client = CloudClient()

    async def execute_pass(self, job: CachedJob):
        # 1. Start recording
        await self.adapter.start_pass_recording()
        
        # 2. Simulate pass duration
        # (In a real system this waits for LOS, but for mock we just proceed)
        
        # 3. Stop recording
        await self.adapter.stop_pass_recording()
        
        # 4. Collect artifacts
        artifacts = await self.adapter.collect_pass_artifacts()
        
        # 5. Build receipt
        receipt_payload = {
            "observation_job_id": str(job.id),
            "status": "COMPLETED",
            "actual_start": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "actual_end": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "carrier_locked": artifacts.get("carrier_locked", False),
            "symbol_locked": artifacts.get("symbol_locked", False),
            "data_volume_bytes": artifacts.get("data_volume_bytes", 0.0),
            "frame_count": artifacts.get("frame_count", 0),
            "average_ebno": artifacts.get("average_ebno", 0.0),
            "tracking_error_summary": artifacts.get("tracking_error_summary", {}),
            "weather_summary": artifacts.get("weather_summary", {}),
            "pass_report_hash": artifacts.get("pass_report_hash", ""),
            "artifact_manifest_hash": artifacts.get("artifact_manifest_hash", ""),
            "notes": "Mock pass execution completed"
        }
        
        # 6. Post receipt to cloud
        await self.client.submit_receipt(receipt_payload)
        return receipt_payload
