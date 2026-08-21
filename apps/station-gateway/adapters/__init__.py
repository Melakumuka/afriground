from .base_adapter import StationGatewayAdapter
from .mock_zodiac_mcs import MockZodiacMCSAdapter

def get_adapter(adapter_type: str) -> StationGatewayAdapter:
    if adapter_type == "mock_zodiac_mcs":
        return MockZodiacMCSAdapter()
    raise ValueError(f"Unknown adapter type: {adapter_type}")
