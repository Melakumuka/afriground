from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from database import Base
import uuid

class Spacecraft(Base):
    """Operational twin of a satellite: separates spacecraft hardware from campaigns."""
    __tablename__ = 'spacecraft'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    satellite_id = Column(UUID(as_uuid=True), ForeignKey('satellites.id'))
    name = Column(String(255), nullable=False)
    norad_id = Column(Integer)
    owner_org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'))
    spacecraft_metadata = Column(JSONB)
    status = Column(String(50), default='operational')  # operational, in_commissioning, decommissioned
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Mission(Base):
    """Operational campaign against a spacecraft."""
    __tablename__ = 'missions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    spacecraft_id = Column(UUID(as_uuid=True), ForeignKey('spacecraft.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    mission_type = Column(String(50), default='earth_observation')  # earth_observation, comms, science, tech_demo
    status = Column(String(50), default='draft')  # draft, active, paused, decommissioned
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MissionProfile(Base):
    """Versioned operational profile of a mission."""
    __tablename__ = 'mission_profiles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey('missions.id'), nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(String(50), default='1.0')
    is_active = Column(Boolean, default=True)
    profile_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MissionRFProfile(Base):
    """RF plan for a mission profile: TX/RX constraints per band."""
    __tablename__ = 'mission_rf_profiles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_profile_id = Column(UUID(as_uuid=True), ForeignKey('mission_profiles.id'), nullable=False)
    band = Column(String(20), nullable=False)  # UHF, S, X, Ku, Ka
    uplink_frequency_hz = Column(Float)
    downlink_frequency_hz = Column(Float)
    uplink_modulation = Column(String(100))
    downlink_modulation = Column(String(100))
    symbol_rate = Column(Float)
    polarization = Column(String(50))
    max_tx_power_dbm = Column(Float)
    is_uplink_enabled = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

class MissionTelemetryDefinition(Base):
    """Decoded TM parameter definition (frame-format-agnostic; XTCE-ready)."""
    __tablename__ = 'mission_telemetry_definitions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_profile_id = Column(UUID(as_uuid=True), ForeignKey('mission_profiles.id'), nullable=False)
    name = Column(String(255), nullable=False)
    parameter_id = Column(String(100), nullable=False)
    data_type = Column(String(50))  # uint8, int16, float32, string, ...
    unit = Column(String(50))
    bit_offset = Column(Integer)
    bit_length = Column(Integer)
    scaling_factor = Column(Float, default=1.0)
    scaling_offset = Column(Float, default=0.0)
    description = Column(Text)

class MissionTelecommandDefinition(Base):
    """Structured telecommand definition for a mission profile."""
    __tablename__ = 'mission_telecommand_definitions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_profile_id = Column(UUID(as_uuid=True), ForeignKey('mission_profiles.id'), nullable=False)
    name = Column(String(255), nullable=False)
    command_code = Column(String(100), nullable=False)
    parameters = Column(JSONB)
    constraints = Column(JSONB)
    description = Column(Text)

class MissionOperationalConstraint(Base):
    """Operational blackout periods, pointing restrictions, station restrictions."""
    __tablename__ = 'mission_operational_constraints'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey('missions.id'), nullable=False)
    constraint_type = Column(String(50), nullable=False)  # blackout_window, sun_pointing, station_restriction, min_elevation
    value = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MissionSLA(Base):
    """SLA requirements attached to a mission."""
    __tablename__ = 'mission_slas'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey('missions.id'), nullable=False)
    sla_type = Column(String(50), nullable=False)  # availability, latency, success_rate, timeliness
    target_value = Column(Float, nullable=False)
    unit = Column(String(50), default='percent')
    reporting_window_days = Column(Integer, default=30)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SLASLAViolation(Base):
    """Recorded SLA breach (Phase 3.0) — created by the runtime on job completion."""
    __tablename__ = 'sla_violations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey('missions.id'), nullable=False)
    observation_job_id = Column(UUID(as_uuid=True), ForeignKey('observation_jobs.id'), nullable=False)
    sla_type = Column(String(50), nullable=False)  # availability, latency, success_rate, timeliness
    target_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    unit = Column(String(50))
    status = Column(String(50), default='open')  # open, acknowledged, resolved, disputed
    violated_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())