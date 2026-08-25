from abc import ABC, abstractmethod
from typing import AsyncIterator


class StationGatewayAdapter(ABC):
    """Abstract base class for interfacing with physical station hardware (MCS, ACU, HDR).

    Per the Safran Pro 730 SX Isolated Observer Profile, this interface is
    **read-only by default**. Active commands (load_mcs_profile, update_acu_tle,
    start/stop_pass_recording, emergency_stow, kill_tx) are retained for
    compatibility but MUST NOT be invoked by the gateway against Safran
    hardware. The mock adapter exercises them for end-to-end testing only.
    """

    # ── Active commands (NOT exercised against real Safran hardware) ──────────

    @abstractmethod
    async def load_mcs_profile(self, profile_payload: dict) -> bool:
        pass

    @abstractmethod
    async def update_acu_tle(self, tle_data: dict) -> bool:
        pass

    @abstractmethod
    async def start_pass_recording(self) -> bool:
        pass

    @abstractmethod
    async def stop_pass_recording(self) -> bool:
        pass

    @abstractmethod
    async def collect_pass_artifacts(self) -> dict:
        pass

    @abstractmethod
    async def emergency_stow(self) -> bool:
        """Command the antenna to immediately stow to safe position.

        NOTE: per the Isolated Observer Profile, the real adapter must NEVER
        implement this for Safran hardware. The Gateway surfaces a passive
        LCB / E-Stop notice to the engineer instead.
        """
        pass

    @abstractmethod
    async def kill_tx(self) -> bool:
        """Immediately kill all RF transmissions.

        NOTE: per the Isolated Observer Profile, the real adapter must NEVER
        implement this for Safran hardware. The HPA radiation mask handles
        muting automatically below the 5° elevation.
        """
        pass

    # ── Passive read methods (Safran Pro 730 SX RM Port 4000 / FTP / etc.) ────

    @abstractmethod
    async def get_station_health(self) -> dict:
        """Returns the extended Safran health snapshot used by the dashboard:
        ACU/HDR/CRT/disk/active-sat-count/LCB engagement/wind/time-sync/elevation mask.
        """
        pass

    @abstractmethod
    async def get_passive_rm_stream(self):  # AsyncIterator[dict]
        """Subscribe to RM Port 4000. Real adapter: open a TCP socket to
        192.168.0.100:4000 (passive, ≤5 concurrent clients). Mock yields one
        sample dict."""
        raise NotImplementedError

    @abstractmethod
    async def pull_ta_xml(self) -> str:
        """FTP pull of the MCS activity table. Returns the file content (XML)."""
        raise NotImplementedError

    @abstractmethod
    async def pull_pass_reports(self, since_iso: str | None = None) -> list:
        """FTP pull of completed pass XML reports from D:\\MCS_PUBLIC\\Pass."""
        raise NotImplementedError

    @abstractmethod
    async def get_disk_usage_percent(self) -> float:
        """Safran PC Saphir D: occupancy percent (0..100)."""
        raise NotImplementedError

    @abstractmethod
    async def get_active_satellite_count(self) -> int:
        """Number of satellites currently active in the MCS MMI."""
        raise NotImplementedError

    @abstractmethod
    async def get_crt_redundancy(self) -> dict:
        """Return CRT redundancy state: {state: 'nominal'|'spare'|'spof'|'unknown',
        nominal_present: bool, spare_present: bool, serial: str}."""
        raise NotImplementedError
