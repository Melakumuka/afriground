"""
Hardware Abstraction Layer (HAL) — Interfaces for Ground Station Edge Equipment.

These abstract interfaces decouple the platform from specific hardware implementations.
Mock implementations allow full development and testing without physical equipment.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel
from datetime import datetime


# ── Data Models ──────────────────────────────────────────────────────────────

class AntennaPosition(BaseModel):
    azimuth_deg: float
    elevation_deg: float
    timestamp: datetime

class RFStatus(BaseModel):
    frequency_mhz: float
    signal_strength_dbm: float
    lock: bool
    modulation: str

class RecordingStatus(BaseModel):
    is_recording: bool
    file_path: Optional[str] = None
    bytes_recorded: int = 0
    duration_seconds: float = 0.0

class WeatherData(BaseModel):
    temperature_c: float
    humidity_pct: float
    wind_speed_kph: float
    wind_direction_deg: float
    rain: bool
    cloud_cover_pct: float
    visibility_km: float
    timestamp: datetime

class PowerStatus(BaseModel):
    main_power: bool
    ups_active: bool
    battery_pct: float
    voltage_v: float


# ── Abstract Interfaces ──────────────────────────────────────────────────────

class AntennaController(ABC):
    """Controls antenna pointing and tracking."""

    @abstractmethod
    async def get_position(self) -> AntennaPosition:
        """Get the current antenna azimuth/elevation."""
        ...

    @abstractmethod
    async def slew_to(self, azimuth: float, elevation: float) -> bool:
        """Command the antenna to slew to a specific position."""
        ...

    @abstractmethod
    async def track_satellite(self, tle_line1: str, tle_line2: str) -> bool:
        """Begin auto-tracking a satellite using its TLE."""
        ...

    @abstractmethod
    async def stop(self) -> bool:
        """Emergency stop / park the antenna."""
        ...

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive antenna status."""
        ...


class RFController(ABC):
    """Controls RF chain configuration."""

    @abstractmethod
    async def set_frequency(self, frequency_mhz: float) -> bool:
        ...

    @abstractmethod
    async def set_modulation(self, modulation: str, symbol_rate: float) -> bool:
        ...

    @abstractmethod
    async def set_polarization(self, polarization: str) -> bool:
        ...

    @abstractmethod
    async def get_status(self) -> RFStatus:
        ...


class ReceiverController(ABC):
    """Controls the receiver/demodulator."""

    @abstractmethod
    async def start_receive(self, frequency_mhz: float, modulation: str) -> bool:
        ...

    @abstractmethod
    async def stop_receive(self) -> bool:
        ...

    @abstractmethod
    async def get_signal_quality(self) -> Dict[str, float]:
        """Returns SNR, BER, Eb/N0 etc."""
        ...


class TransmitterController(ABC):
    """Controls the transmitter for uplink/TT&C."""

    @abstractmethod
    async def start_transmit(self, frequency_mhz: float, power_dbm: float) -> bool:
        ...

    @abstractmethod
    async def stop_transmit(self) -> bool:
        ...

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        ...


class ModemController(ABC):
    """Controls the modem for data encoding/decoding."""

    @abstractmethod
    async def configure(self, config: Dict[str, Any]) -> bool:
        ...

    @abstractmethod
    async def get_bitstream_stats(self) -> Dict[str, Any]:
        """Returns frame count, error rate, throughput."""
        ...


class SDRController(ABC):
    """Controls Software Defined Radio equipment."""

    @abstractmethod
    async def configure_channel(self, center_freq_mhz: float, bandwidth_mhz: float) -> bool:
        ...

    @abstractmethod
    async def get_spectrum(self, span_mhz: float) -> Dict[str, Any]:
        """Returns spectrum analysis data."""
        ...


class WeatherController(ABC):
    """Reads weather station data for risk assessment."""

    @abstractmethod
    async def get_current(self) -> WeatherData:
        ...

    @abstractmethod
    async def is_safe_for_operations(self) -> bool:
        """Returns True if weather conditions permit antenna operations."""
        ...


class PowerController(ABC):
    """Monitors and controls power systems."""

    @abstractmethod
    async def get_status(self) -> PowerStatus:
        ...

    @abstractmethod
    async def switch_to_ups(self) -> bool:
        ...


class RecordingController(ABC):
    """Controls data recording to disk."""

    @abstractmethod
    async def start_recording(self, output_path: str) -> bool:
        ...

    @abstractmethod
    async def stop_recording(self) -> RecordingStatus:
        ...

    @abstractmethod
    async def get_status(self) -> RecordingStatus:
        ...
