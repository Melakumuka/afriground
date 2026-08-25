import asyncio
import logging
import random
from datetime import datetime, timezone
from typing import AsyncIterator

from .base_adapter import StationGatewayAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockZodiacMCSAdapter(StationGatewayAdapter):
    """Mock implementation of the Safran Pro 730 SX / Zodiac PFM730 MCS adapter.

    Simulates passive RM Port 4000 telemetry, FTP activity table pulls, and
    the SPOF CRT redundancy state. Used for development, testing, CI, and
    demo mode. Never issues real commands to the Safran subnet.
    """

    def __init__(self) -> None:
        self._crt_serial = "19019"
        self._crt_state = "nominal"  # toggle to "spare" or "spof" via toggle_crt_state

    # ── Active commands (mock only; not exercised against real hardware) ──────

    async def load_mcs_profile(self, profile_payload: dict) -> bool:
        logger.info(f"[MOCK MCS] Loading MCS profile with payload: {profile_payload}")
        return True

    async def update_acu_tle(self, tle_data: dict) -> bool:
        logger.info(f"[MOCK ACU] Updating TLE with data: {tle_data}")
        return True

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
            "data_volume_bytes": 1024 * 1024 * 500.0,
            "frame_count": 15000,
            "average_ebno": 12.4,
            "tracking_error_summary": {"max_az": 0.1, "max_el": 0.05, "mean_az": 0.02, "mean_el": 0.01},
            "pass_report_hash": "mock_hash_8a9b",
            "artifact_manifest_hash": "mock_manifest_hash_1c2d",
            "weather_summary": {"wind_speed": 15, "temperature": 22, "humidity": 45},
        }

    async def emergency_stow(self) -> bool:
        logger.critical("[MOCK ACU] (not exercised against real Safran hardware)")
        return True

    async def kill_tx(self) -> bool:
        logger.critical("[MOCK RF] (not exercised against real Safran hardware)")
        return True

    # ── Passive read methods (Safran Pro 730 SX) ──────────────────────────────

    async def get_station_health(self) -> dict:
        """Extended Safran health snapshot for the dashboard."""
        wind = random.uniform(5, 30)
        offset = random.uniform(-100, 100)
        return {
            # legacy fields
            "acu_status": "READY",
            "hdr_status": "LOCKED",
            "wind_speed_kmh": wind,
            "time_sync": "SYNCED",
            "weather_safe": wind < 40,
            # new Safran-specific fields
            "mcs_link_up": True,
            "mcs_last_packet_age_s": random.randint(0, 3),
            "acu_mode": "ephemeris",
            "elevation_mask_deg": 5.0,
            "crt_redundancy": await self.get_crt_redundancy(),
            "disk_usage_percent": random.uniform(40, 70),
            "active_satellite_count": random.randint(2, 8),
            "lcb_engaged": False,
            "clock_offset_ms": offset,
        }

    async def get_passive_rm_stream(self) -> AsyncIterator[dict]:
        """Mock RM Port 4000 stream — yields one Az/El sample."""
        sample = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "az_deg": random.uniform(0, 360),
            "el_deg": random.uniform(5, 90),
            "carrier_lock": True,
            "symbol_lock": True,
            "eb_no_db": round(random.uniform(8, 16), 2),
        }
        yield sample

    async def pull_ta_xml(self) -> str:
        """Mock activity table XML."""
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<ActivityTable station="PRO730-SN004">\n'
            '  <Pass id="mock-1" sat="MOCK-SAT" aos="2026-01-01T00:00:00Z" los="2026-01-01T00:15:00Z"/>\n'
            '</ActivityTable>\n'
        )

    async def pull_pass_reports(self, since_iso: str | None = None) -> list:
        """Mock list of completed-pass report XML files."""
        return []

    async def get_disk_usage_percent(self) -> float:
        return random.uniform(40, 70)

    async def get_active_satellite_count(self) -> int:
        return random.randint(2, 8)

    async def get_crt_redundancy(self) -> dict:
        if self._crt_state == "spof":
            return {
                "state": "spof",
                "nominal_present": False,
                "spare_present": False,
                "serial": None,
                "note": "S-band TX #2 non-functional; no spare in unit.",
            }
        if self._crt_state == "spare":
            return {
                "state": "spare",
                "nominal_present": False,
                "spare_present": True,
                "serial": "TEMP-Spare",
                "note": "Spare CRT in use; nominal S/N 19019 defective; no hot-standby.",
            }
        return {
            "state": "nominal",
            "nominal_present": True,
            "spare_present": True,
            "serial": self._crt_serial,
            "note": "Nominal CRT with hot-standby spare.",
        }

    # ── Test helpers ──────────────────────────────────────────────────────────

    def toggle_crt_state(self, state: str) -> None:
        """Test helper: set CRT state to 'nominal' | 'spare' | 'spof'."""
        assert state in ("nominal", "spare", "spof")
        self._crt_state = state
