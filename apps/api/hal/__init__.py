"""
HAL — Hardware Abstraction Layer package.

Provides a factory to get controller instances based on environment configuration.
In development, all controllers return Mock implementations.
"""
from hal.interfaces import (
    AntennaController,
    RFController,
    ReceiverController,
    TransmitterController,
    ModemController,
    SDRController,
    WeatherController,
    PowerController,
    RecordingController,
)
from hal.mock_controllers import (
    MockAntennaController,
    MockRFController,
    MockReceiverController,
    MockTransmitterController,
    MockModemController,
    MockSDRController,
    MockWeatherController,
    MockPowerController,
    MockRecordingController,
)


class EdgeNodeFactory:
    """
    Factory for creating hardware controller instances.
    In development, returns mock controllers.
    In production, would return real hardware-specific implementations.
    """

    def __init__(self, mode: str = "mock"):
        self.mode = mode

    def get_antenna_controller(self) -> AntennaController:
        if self.mode == "mock":
            return MockAntennaController()
        raise NotImplementedError(f"No antenna controller for mode '{self.mode}'")

    def get_rf_controller(self) -> RFController:
        if self.mode == "mock":
            return MockRFController()
        raise NotImplementedError(f"No RF controller for mode '{self.mode}'")

    def get_receiver_controller(self) -> ReceiverController:
        if self.mode == "mock":
            return MockReceiverController()
        raise NotImplementedError(f"No receiver controller for mode '{self.mode}'")

    def get_transmitter_controller(self) -> TransmitterController:
        if self.mode == "mock":
            return MockTransmitterController()
        raise NotImplementedError(f"No transmitter controller for mode '{self.mode}'")

    def get_modem_controller(self) -> ModemController:
        if self.mode == "mock":
            return MockModemController()
        raise NotImplementedError(f"No modem controller for mode '{self.mode}'")

    def get_sdr_controller(self) -> SDRController:
        if self.mode == "mock":
            return MockSDRController()
        raise NotImplementedError(f"No SDR controller for mode '{self.mode}'")

    def get_weather_controller(self) -> WeatherController:
        if self.mode == "mock":
            return MockWeatherController()
        raise NotImplementedError(f"No weather controller for mode '{self.mode}'")

    def get_power_controller(self) -> PowerController:
        if self.mode == "mock":
            return MockPowerController()
        raise NotImplementedError(f"No power controller for mode '{self.mode}'")

    def get_recording_controller(self) -> RecordingController:
        if self.mode == "mock":
            return MockRecordingController()
        raise NotImplementedError(f"No recording controller for mode '{self.mode}'")
