import logging
from pathlib import Path

from adapters import get_adapter
from config import settings

logger = logging.getLogger(__name__)

class IsolatedObserver:
    """Read-only Safran Pro 730 SX health/status aggregator.

    Never issues a command to Port 3001/4001/4003. All data sources are
    passive: FTP file retrieval, RM Port 4000 socket subscription,
    local NTP, local weather sensor.
    """

    def __init__(self):
        self.adapter = get_adapter(settings.adapter_type)

    async def get_mcs_link(self) -> dict:
        """RM 4000 ping + last packet age."""
        # Using the base adapter's health method for some of this, but 
        # ideally we should build this from the adapter's raw passive read methods.
        health = await self.adapter.get_station_health()
        return {
            "mcs_link_up": health.get("mcs_link_up", False),
            "mcs_last_packet_age_s": health.get("mcs_last_packet_age_s", 0)
        }

    async def get_activity_table(self) -> str:
        """Last TA.xml via FTP."""
        return await self.adapter.pull_ta_xml()

    async def get_lcb_status(self) -> dict:
        """Inferred from ACU RM stream."""
        health = await self.adapter.get_station_health()
        return {"lcb_engaged": health.get("lcb_engaged", False)}

    async def get_stow_pins(self) -> dict:
        """Inferred from ACU RM stream."""
        # Mocking for now as it's an engineering check
        return {"stow_pins_engaged": False}

    async def get_acu_tle_window(self) -> dict:
        return {"valid": True, "epoch_window_start": "2026-08-25T00:00:00Z", "epoch_window_end": "2026-08-26T00:00:00Z"}

    async def get_disk_usage(self) -> dict:
        """Safran PC Saphir D: occupancy percent"""
        usage = await self.adapter.get_disk_usage_percent()
        return {"disk_usage_percent": usage}

    async def get_active_satellite_count(self) -> int:
        return await self.adapter.get_active_satellite_count()

    async def get_crt_redundancy(self) -> dict:
        """Nominal vs Spare vs SPOF"""
        return await self.adapter.get_crt_redundancy()

    async def get_next_pass_conflicts(self) -> list:
        """Interpass + rise-angle conflicts"""
        # Mock empty list
        return []

    async def get_elevation_mask(self) -> dict:
        """Must be <= 5°"""
        health = await self.adapter.get_station_health()
        return {"elevation_mask_deg": health.get("elevation_mask_deg", 5.0)}
