from abc import ABC, abstractmethod

class StationGatewayAdapter(ABC):
    """Abstract base class for interfacing with physical station hardware (MCS, ACU, HDR)."""

    @abstractmethod
    async def load_mcs_profile(self, profile_payload: dict) -> bool:
        pass

    @abstractmethod
    async def update_acu_tle(self, tle_data: dict) -> bool:
        pass

    @abstractmethod
    async def get_station_health(self) -> dict:
        """Returns ACU, HDR, Wind, Time status."""
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
