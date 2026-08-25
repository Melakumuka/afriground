import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Station Identity ──────────────────────────────────────────────────────
    station_id: str = os.getenv("STATION_ID", "00000000-0000-0000-0000-000000000000")
    agent_id: str = os.getenv("AGENT_ID", "gateway-01")
    agent_version: str = os.getenv("AGENT_VERSION", "1.0.0")
    station_serial: str = os.getenv("STATION_SERIAL", "PRO730-SX-SN004")

    # ── Cloud Connection ──────────────────────────────────────────────────────
    cloud_api_url: str = os.getenv("CLOUD_API_URL", "http://localhost:8000")
    cloud_api_key: str = os.getenv("CLOUD_API_KEY", "dummy-key")

    # ── Local Hardware Adapter ────────────────────────────────────────────────
    # Available: "mock_zodiac_mcs", "zodiac_mcs", "safran_pro730"
    adapter_type: str = os.getenv("ADAPTER_TYPE", "mock_zodiac_mcs")

    # ── Local Persistence ─────────────────────────────────────────────────────
    sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", "sqlite+aiosqlite:///./gateway.db")

    # ── Safran Pro 730 SX Site Thresholds (configurable per station) ──────────
    wind_safe_kmh: float = float(os.getenv("WIND_SAFE_KMH", "40"))
    wind_warning_kmh: float = float(os.getenv("WIND_WARNING_KMH", "55"))
    hpa_radiation_mask_deg: float = float(os.getenv("HPA_RADIATION_MASK_DEG", "5"))
    disk_warn_percent: float = float(os.getenv("DISK_WARN_PERCENT", "75"))
    disk_reject_percent: float = float(os.getenv("DISK_REJECT_PERCENT", "80"))
    mmi_satellite_limit: int = int(os.getenv("MMI_SATELLITE_LIMIT", "12"))
    mmi_satellite_warn: int = int(os.getenv("MMI_SATELLITE_WARN", "10"))

    # ── Firewall Verification ─────────────────────────────────────────────────
    firewall_expected_rules: str = os.getenv(
        "FIREWALL_EXPECTED_RULES",
        "AfriGround_Gateway_-Block-4001:Block:4001,"
        "AfriGround_Gateway_-Block-4003:Block:4003,"
        "AfriGround_Gateway_-Allow-4000:Allow:4000,"
        "AfriGround_Gateway_-Allow-20:Allow:20,"
        "AfriGround_Gateway_-Allow-21:Allow:21,"
        "AfriGround_Gateway_-Allow-Cloud-443:Allow:443,"
        "AfriGround_Gateway_-Isolate-Subnet:Block:any",
    )

    # ── Adapter Network Targets (for firewall verify on real deployments) ──────
    mcs_ip: str = os.getenv("MCS_IP", "192.168.0.100")
    safran_subnet: str = os.getenv("SAFRAN_SUBNET", "192.168.0.0/24")

    class Config:
        env_file = ".env"


settings = Settings()
