"""
Hardware Abstraction Layer — Mock implementations for development and testing.

These mock controllers simulate real hardware behavior, allowing the entire
platform to be developed, tested, and demonstrated without physical equipment.
"""
import random
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from hal.interfaces import (
    AntennaController, AntennaPosition,
    RFController, RFStatus,
    ReceiverController,
    TransmitterController,
    ModemController,
    SDRController,
    WeatherController, WeatherData,
    PowerController, PowerStatus,
    RecordingController, RecordingStatus,
)


class MockAntennaController(AntennaController):
    def __init__(self):
        self._azimuth = 0.0
        self._elevation = 90.0  # parked position
        self._tracking = False

    async def get_position(self) -> AntennaPosition:
        return AntennaPosition(
            azimuth_deg=self._azimuth,
            elevation_deg=self._elevation,
            timestamp=datetime.now(timezone.utc),
        )

    async def slew_to(self, azimuth: float, elevation: float) -> bool:
        await asyncio.sleep(0.1)  # simulate motor movement
        self._azimuth = azimuth
        self._elevation = elevation
        return True

    async def track_satellite(self, tle_line1: str, tle_line2: str) -> bool:
        self._tracking = True
        # Simulate initial acquisition
        self._azimuth = random.uniform(0, 360)
        self._elevation = random.uniform(5, 85)
        return True

    async def stop(self) -> bool:
        self._tracking = False
        self._elevation = 90.0
        return True

    async def get_status(self) -> Dict[str, Any]:
        return {
            "azimuth": self._azimuth,
            "elevation": self._elevation,
            "tracking": self._tracking,
            "health": "nominal",
        }


class MockRFController(RFController):
    def __init__(self):
        self._freq = 0.0
        self._mod = "QPSK"
        self._pol = "RHCP"

    async def set_frequency(self, frequency_mhz: float) -> bool:
        self._freq = frequency_mhz
        return True

    async def set_modulation(self, modulation: str, symbol_rate: float) -> bool:
        self._mod = modulation
        return True

    async def set_polarization(self, polarization: str) -> bool:
        self._pol = polarization
        return True

    async def get_status(self) -> RFStatus:
        return RFStatus(
            frequency_mhz=self._freq,
            signal_strength_dbm=random.uniform(-80, -40),
            lock=self._freq > 0,
            modulation=self._mod,
        )


class MockReceiverController(ReceiverController):
    def __init__(self):
        self._receiving = False

    async def start_receive(self, frequency_mhz: float, modulation: str) -> bool:
        self._receiving = True
        return True

    async def stop_receive(self) -> bool:
        self._receiving = False
        return True

    async def get_signal_quality(self) -> Dict[str, float]:
        if not self._receiving:
            return {"snr_db": 0, "ber": 1.0, "eb_n0": 0}
        return {
            "snr_db": random.uniform(8, 25),
            "ber": random.uniform(1e-9, 1e-6),
            "eb_n0": random.uniform(6, 20),
        }


class MockTransmitterController(TransmitterController):
    def __init__(self):
        self._transmitting = False

    async def start_transmit(self, frequency_mhz: float, power_dbm: float) -> bool:
        self._transmitting = True
        return True

    async def stop_transmit(self) -> bool:
        self._transmitting = False
        return True

    async def get_status(self) -> Dict[str, Any]:
        return {"transmitting": self._transmitting, "reflected_power_dbm": -30}


class MockModemController(ModemController):
    async def configure(self, config: Dict[str, Any]) -> bool:
        return True

    async def get_bitstream_stats(self) -> Dict[str, Any]:
        return {
            "frames_received": random.randint(1000, 50000),
            "frames_errors": random.randint(0, 5),
            "throughput_kbps": random.uniform(100, 500),
        }


class MockSDRController(SDRController):
    async def configure_channel(self, center_freq_mhz: float, bandwidth_mhz: float) -> bool:
        return True

    async def get_spectrum(self, span_mhz: float) -> Dict[str, Any]:
        return {
            "center_freq_mhz": 2200,
            "span_mhz": span_mhz,
            "peak_dbm": random.uniform(-60, -30),
            "noise_floor_dbm": -90,
        }


class MockWeatherController(WeatherController):
    async def get_current(self) -> WeatherData:
        return WeatherData(
            temperature_c=random.uniform(10, 28),
            humidity_pct=random.uniform(20, 70),
            wind_speed_kph=random.uniform(0, 30),
            wind_direction_deg=random.uniform(0, 360),
            rain=random.random() < 0.1,
            cloud_cover_pct=random.uniform(0, 50),
            visibility_km=random.uniform(5, 20),
            timestamp=datetime.now(timezone.utc),
        )

    async def is_safe_for_operations(self) -> bool:
        weather = await self.get_current()
        return not weather.rain and weather.wind_speed_kph < 60


class MockPowerController(PowerController):
    async def get_status(self) -> PowerStatus:
        return PowerStatus(
            main_power=True,
            ups_active=False,
            battery_pct=100.0,
            voltage_v=220.0,
        )

    async def switch_to_ups(self) -> bool:
        return True


class MockRecordingController(RecordingController):
    def __init__(self):
        self._recording = False
        self._bytes = 0

    async def start_recording(self, output_path: str) -> bool:
        self._recording = True
        self._bytes = 0
        return True

    async def stop_recording(self) -> RecordingStatus:
        self._recording = False
        final = RecordingStatus(
            is_recording=False,
            file_path="/data/recordings/mock_capture.raw",
            bytes_recorded=self._bytes or random.randint(50_000_000, 500_000_000),
            duration_seconds=random.uniform(300, 900),
        )
        return final

    async def get_status(self) -> RecordingStatus:
        if self._recording:
            self._bytes += random.randint(1_000_000, 10_000_000)
        return RecordingStatus(
            is_recording=self._recording,
            bytes_recorded=self._bytes,
        )
