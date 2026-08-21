import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Station Identity
    station_id: str = os.getenv("STATION_ID", "00000000-0000-0000-0000-000000000000")
    agent_id: str = os.getenv("AGENT_ID", "gateway-01")
    agent_version: str = "1.0.0"

    # Cloud Connection
    cloud_api_url: str = os.getenv("CLOUD_API_URL", "http://localhost:8000")
    cloud_api_key: str = os.getenv("CLOUD_API_KEY", "dummy-key")

    # Local Hardware Adapter
    # Available: "mock_zodiac_mcs", "zodiac_mcs"
    adapter_type: str = os.getenv("ADAPTER_TYPE", "mock_zodiac_mcs")

    # Local Persistence
    sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", "sqlite+aiosqlite:///./gateway.db")

    class Config:
        env_file = ".env"

settings = Settings()
