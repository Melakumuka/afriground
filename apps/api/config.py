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

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
