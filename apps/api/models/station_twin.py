from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from database import Base
import uuid

class StationCapability(Base):
    """Structured RF capability of a station (replaces loose JSONB)."""
    __tablename__ = 'station_capabilities'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    band = Column(String(20), nullable=False)
    frequency_min_hz = Column(Float, nullable=False)
    frequency_max_hz = Column(Float, nullable=False)
    polarization = Column(String(50))
    max_tx_power_dbm = Column(Float)
    tx_authorized = Column(Boolean, default=False)
    gain_dbi = Column(Float)
    noise_figure_db = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class StationHardware(Base):
    """Tracked physical hardware at a station (antenna, SDR, rotator, clock, ...)."""
    __tablename__ = 'station_hardware'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    hardware_type = Column(String(50), nullable=False)  # antenna, sdr, rotator, clock, amplifier, lnb
    model = Column(String(255))
    serial_number = Column(String(255))
    firmware_version = Column(String(100))
    status = Column(String(50), default='operational')  # operational, degraded, offline, retired
    installed_at = Column(DateTime(timezone=True))
    last_maintenance_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class StationLicense(Base):
    """Regulatory license held by the station operator."""
    __tablename__ = 'station_licenses'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    license_type = Column(String(50), nullable=False)  # uplink, downlink, amateur, experimental
    issuing_authority = Column(String(255), nullable=False)
    license_number = Column(String(255))
    country = Column(String(100))
    frequency_bands = Column(JSONB)
    max_power_dbm = Column(Float)
    issued_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    status = Column(String(50), default='valid')  # valid, expired, suspended, revoked
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class StationCertification(Base):
    """Current certification state of a station (Digital Twin lifecycle)."""
    __tablename__ = 'station_certifications'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    cert_type = Column(String(50), default='operational')
    current_state = Column(String(50), default='REGISTERED')  # REGISTERED, PROVISIONING, VALIDATING, CERTIFIED, DECERTIFIED, REJECTED
    cert_version = Column(String(20), default='1.0')
    certified_at = Column(DateTime(timezone=True))
    valid_until = Column(DateTime(timezone=True))
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class StationCertificationEvent(Base):
    """Auditable certification state transitions."""
    __tablename__ = 'station_certification_events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    from_state = Column(String(50))
    to_state = Column(String(50), nullable=False)
    transition_reason = Column(Text)
    initiated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class StationQualityScore(Base):
    """Periodic quality scoring for a station (feeds routing/risk)."""
    __tablename__ = 'station_quality_scores'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    score = Column(Float, nullable=False)
    availability = Column(Float)
    reliability = Column(Float)
    timeliness = Column(Float)
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

class StationTimeStatus(Base):
    """Time synchronization quality reported by the station agent."""
    __tablename__ = 'station_time_statuses'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    sync_status = Column(String(50), default='UNSYNCED')  # SYNCED, SYNCING, UNSYNCED, DEGRADED
    offset_ms = Column(Float)
    last_sync_at = Column(DateTime(timezone=True))
    clock_source = Column(String(100))
    reported_at = Column(DateTime(timezone=True), server_default=func.now())

class StationAgentIdentity(Base):
    """Edge agent identity for a station (mTLS bridge, Phase 4.0)."""
    __tablename__ = 'station_agent_identities'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    agent_id = Column(String(255), nullable=False)
    agent_version = Column(String(100))
    public_key_pem = Column(Text)
    certificate_serial = Column(String(255))
    certificate_valid_until = Column(DateTime(timezone=True))
    last_heartbeat_at = Column(DateTime(timezone=True))
    revoked_at = Column(DateTime(timezone=True))
    status = Column(String(50), default='active')  # active, inactive, revoked
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class StationHeartbeat(Base):
    """Per-agent heartbeat records used by the missed-heartbeat watchdog."""
    __tablename__ = 'station_heartbeats'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    agent_id = Column(String(255), nullable=False)
    agent_version = Column(String(100))
    metrics = Column(JSONB)
    received_at = Column(DateTime(timezone=True), server_default=func.now())

class StationTelemetryReading(Base):
    """Structured telemetry readings reported by station agents."""
    __tablename__ = 'station_telemetry_readings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    agent_id = Column(String(255), nullable=False)
    telemetry_type = Column(String(50), nullable=False)  # antenna, rf, signal, weather, power, recording
    payload = Column(JSONB)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

class StationOperationProfile(Base):
    """Saved, certified station configuration for a specific satellite mission.
    Station-Led Configuration: engineers configure expensive hardware (MCS, HDR,
    ACU, RF chain) once per satellite.  Normal passes load this profile, update
    only TLE/timing, and present a readiness checklist.

    See docs/PFM730_INTEGRATION.md for payload schema reference.
    See docs/STATION_ONBOARDING.md §2 for the configure-once workflow."""
    __tablename__ = 'station_operation_profiles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    mission_profile_id = Column(UUID(as_uuid=True), ForeignKey('mission_profiles.id'), nullable=False)
    satellite_id = Column(UUID(as_uuid=True), ForeignKey('spacecraft.id'))
    name = Column(String(255), nullable=False)

    # ── Certification lifecycle ──────────────────────────────────────────────
    # CONFIGURING → TESTING → QUALIFICATION_PASSED → CERTIFIED → SUSPENDED / RETIRED
    status = Column(String(50), default='CONFIGURING')
    certification_state = Column(String(50), default='CONFIGURING')
    certified_at = Column(DateTime(timezone=True))
    certified_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    qualification_job_id = Column(UUID(as_uuid=True), ForeignKey('observation_jobs.id'))

    # ── Operation mode ───────────────────────────────────────────────────────
    # MANUAL_CONFIRMED (default for PFM730): engineer must click CONFIRM READY.
    # SEMI_AUTOMATIC: auto-confirm if all pre-flight checks pass.
    # AUTOMATIC: no confirmation needed (e.g. SatNOGS stations).
    operation_mode = Column(String(50), default='MANUAL_CONFIRMED')

    # ── Equipment configuration payloads (JSONB) ────────────────────────────
    mcs_profile_payload = Column(JSONB)      # Zodiac PFM730 MCS mission/preset
    hdr_config_payload = Column(JSONB)       # CORTEX HDR modem (IF, symbol rate, coding, frame)
    acu_config_payload = Column(JSONB)       # ACU satellite preset (tracking, polarization, masks)
    rf_path_payload = Column(JSONB)          # RF chain (LNB, LNA, IF, filter, polarization)
    decoder_config_payload = Column(JSONB)   # Frame processing (VCID filter, output format)
    safety_payload = Column(JSONB)           # Wind limits, timeout thresholds, interlock config

    # ── Usage tracking ───────────────────────────────────────────────────────
    success_rate = Column(Float)             # rolling success rate from execution receipts
    total_passes = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())