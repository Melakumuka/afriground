import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime

from config import settings

engine = create_async_engine(settings.sqlite_db_path, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class CachedProfile(Base):
    __tablename__ = "cached_profiles"
    id = Column(String, primary_key=True)
    name = Column(String)
    satellite_id = Column(String, nullable=True)
    operation_mode = Column(String)
    mcs_profile_payload = Column(String) # JSON string
    hdr_config_payload = Column(String) # JSON string
    acu_config_payload = Column(String) # JSON string

class CachedJob(Base):
    __tablename__ = "cached_jobs"
    id = Column(String, primary_key=True)
    status = Column(String)
    readiness_status = Column(String)
    mission_profile_id = Column(String)
    station_operation_profile_id = Column(String, nullable=True)
    priority = Column(Integer)
    tx_requested = Column(Integer)
    scheduled_start = Column(DateTime(timezone=True), nullable=True)
    scheduled_end = Column(DateTime(timezone=True), nullable=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
