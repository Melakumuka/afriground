import logging
from .base_adapter import StationGatewayAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockZodiacMCSAdapter(StationGatewayAdapter):
    """Mock implementation of the Zodiac PFM730 MCS adapter."""
    
    async def load_mcs_profile(self, profile_payload: dict) -> bool:
        logger.info(f"[MOCK MCS] Loading MCS profile with payload: {profile_payload}")
        return True

    async def update_acu_tle(self, tle_data: dict) -> bool:
        logger.info(f"[MOCK ACU] Updating TLE with data: {tle_data}")
        return True

    async def get_station_health(self) -> dict:
        logger.info("[MOCK HEALTH] Fetching station health")
        return {
            "acu_status": "READY",
            "hdr_status": "LOCKED",
            "wind_speed_kmh": 15,
            "time_sync": "SYNCED",
            "weather_safe": True
        }

    async def start_pass_recording(self) -> bool:
        logger.info("[MOCK MCS] Starting pass recording...")
        return True

    async def stop_pass_recording(self) -> bool:
        logger.info("[MOCK MCS] Stopping pass recording...")
        return True

    async def collect_pass_artifacts(self) -> dict:
        logger.info("[MOCK MCS] Collecting pass artifacts...")
        return {
            "carrier_locked": True,
            "symbol_locked": True,
            "data_volume_bytes": 1024 * 1024 * 500.0, # 500 MB
            "frame_count": 15000,
            "average_ebno": 12.4,
            "tracking_error_summary": {"max_az": 0.1, "max_el": 0.05, "mean_az": 0.02, "mean_el": 0.01},
            "pass_report_hash": "mock_hash_8a9b",
            "artifact_manifest_hash": "mock_manifest_hash_1c2d",
            "weather_summary": {"wind_speed": 15, "temperature": 22, "humidity": 45}
        }
