import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text

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
    status = Column(String, default="UNKNOWN")        # certification state from cloud
    certification_state = Column(String, default="UNKNOWN")
    mcs_profile_payload = Column(String)               # JSON string
    hdr_config_payload = Column(String)                # JSON string
    acu_config_payload = Column(String)                # JSON string
    rf_path_payload = Column(String)                   # JSON string
    decoder_config_payload = Column(String)            # JSON string
    safety_payload = Column(String)                    # JSON string


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
    rise_angle_deg = Column(String, nullable=True)
    planned_min_elevation_deg = Column(String, nullable=True)
    interpass_gap_seconds = Column(String, nullable=True)


class FirewallAuditLog(Base):
    """Per-rule firewall posture audit. Local-first; never assumes cloud."""
    __tablename__ = "firewall_audit_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime(timezone=True))
    rule_name = Column(String)
    present = Column(Boolean)
    enabled = Column(Boolean)
    direction = Column(String, nullable=True)
    action = Column(String, nullable=True)
    remote_port = Column(String, nullable=True)
    expected_action = Column(String, nullable=True)
    direction_correct = Column(Boolean, default=True)


class LCBEngagementLog(Base):
    """Local Control Box (hand-paddle) engagement log."""
    __tablename__ = "lcb_engagement_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime(timezone=True))
    job_id = Column(String)
    lcb_state = Column(Boolean)            # True = engaged
    source = Column(String)                 # "rm_stream", "engineer_ack"


class CRTRedundancyLog(Base):
    """CRT (S/N 19019) redundancy state log."""
    __tablename__ = "crt_redundancy_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime(timezone=True))
    nominal_present = Column(Boolean)
    spare_present = Column(Boolean)
    spof_declared = Column(Boolean)
    source = Column(String, default="rm_stream")


class LocalActionAck(Base):
    """Engineer acknowledgement of the passive / no-active-commands notice."""
    __tablename__ = "local_action_ack"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime(timezone=True))
    job_id = Column(String)
    ack_text = Column(String, default="Local Action Procedure Reviewed")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
