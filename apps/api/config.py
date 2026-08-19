import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AfriGround API"
    app_env: str = "development"
    debug: bool = True
    secret_key: str
    api_cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Database
    database_url: str
    test_database_url: str = "postgresql+asyncpg://afriground:afriground_dev_password@localhost:5433/afriground_test"
    
    # Supabase Auth
    supabase_url: str
    supabase_service_role_key: str
    supabase_jwt_secret: str
    
    # Redis
    redis_url: str

    # Phase 2.0 — Orchestration runtime
    celery_broker_url: str = "redis://localhost:6379/0"
    outbox_poll_interval: float = 5.0
    outbox_retry_base_s: float = 5.0
    outbox_retry_max_s: float = 3600.0

    # Phase 2.1 — Edge agent watchdog
    heartbeat_check_interval_s: float = 60.0
    heartbeat_threshold_s: float = 120.0

    # Phase 3.0 — Commercial / recurring missions
    recurring_sweep_interval_s: float = 3600.0

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
