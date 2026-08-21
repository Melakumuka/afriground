from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Float, Integer, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from database import Base
import uuid

class VisibilityOpportunity(Base):
    """Raw geometric pass: a spacecraft is geometrically visible from a station."""
    __tablename__ = 'visibility_opportunities'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    spacecraft_id = Column(UUID(as_uuid=True), ForeignKey('spacecraft.id'), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    pass_prediction_id = Column(UUID(as_uuid=True), ForeignKey('pass_predictions.id'))
    aos = Column(DateTime(timezone=True), nullable=False)
    los = Column(DateTime(timezone=True), nullable=False)
    max_elevation_deg = Column(Float, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    status = Column(String(50), default='OPEN')  # OPEN, PROMOTED, EXPIRED, CANCELLED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ContactOpportunity(Base):
    """A feasible RF contact opportunity for a mission profile on a specific pass."""
    __tablename__ = 'contact_opportunities'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    visibility_opportunity_id = Column(UUID(as_uuid=True), ForeignKey('visibility_opportunities.id'), nullable=False)
    mission_profile_id = Column(UUID(as_uuid=True), ForeignKey('mission_profiles.id'), nullable=False)
    rf_profile_id = Column(UUID(as_uuid=True), ForeignKey('mission_rf_profiles.id'))
    required_band = Column(String(20))
    min_elevation_deg = Column(Float)
    estimated_duration_seconds = Column(Integer)
    opportunity_score = Column(Float)
    status = Column(String(50), default='OPEN')  # OPEN, RESERVED, CLOSED, EXPIRED, CANCELLED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Reservation(Base):
    """Customer reservation against a contact opportunity."""
    __tablename__ = 'reservations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    contact_opportunity_id = Column(UUID(as_uuid=True), ForeignKey('contact_opportunities.id'), nullable=False)
    customer_org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    spacecraft_id = Column(UUID(as_uuid=True), ForeignKey('spacecraft.id'), nullable=False)
    mission_id = Column(UUID(as_uuid=True), ForeignKey('missions.id'))
    status = Column(String(50), default='REQUESTED')  # REQUESTED, RESERVED, CONFIRMED, CANCELLED, EXPIRED
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScheduledContact(Base):
    """A confirmed, executable contact on the station schedule."""
    __tablename__ = 'scheduled_contacts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey('reservations.id'), nullable=False)
    contact_opportunity_id = Column(UUID(as_uuid=True), ForeignKey('contact_opportunities.id'), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'), nullable=False)
    spacecraft_id = Column(UUID(as_uuid=True), ForeignKey('spacecraft.id'), nullable=False)
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default='CONFIRMED')  # CONFIRMED, IN_PROGRESS, COMPLETED, CANCELLED, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ObservationJob(Base):
    """Executable unit of work for the orchestrator / edge agent."""
    __tablename__ = 'observation_jobs'
    __table_args__ = (
        Index('idx_jobs_readiness', 'readiness_status'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'), nullable=False)
    scheduled_contact_id = Column(UUID(as_uuid=True), ForeignKey('scheduled_contacts.id'), nullable=False)
    mission_profile_id = Column(UUID(as_uuid=True), ForeignKey('mission_profiles.id'), nullable=False)
    station_operation_profile_id = Column(UUID(as_uuid=True), ForeignKey('station_operation_profiles.id'))
    status = Column(String(50), default='DRAFT', nullable=False)
    readiness_status = Column(String(50), default='PENDING')  # PENDING, READY, NOT_READY
    state_machine_version = Column(String(20), default='1.0')
    priority = Column(Integer, default=5)
    tx_requested = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=2)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    failure_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ExecutionReceipt(Base):
    """Post-execution result report for an observation job.
    Generated by the Edge Agent after pass completion.  Contains structured
    telemetry from the PFM730 subsystems and cryptographic attestation hashes.
    See docs/PFM730_INTEGRATION.md §8 for field reference."""
    __tablename__ = 'execution_receipts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    observation_job_id = Column(UUID(as_uuid=True), ForeignKey('observation_jobs.id'), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'))
    profile_id = Column(UUID(as_uuid=True), ForeignKey('station_operation_profiles.id'))
    receipt_version = Column(String(20), default='1.0')
    status = Column(String(50), nullable=False)  # COMPLETED, PARTIAL_SUCCESS, FAILED

    # ── Pass timing ──────────────────────────────────────────────────────────
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))

    # ── RF / modem quality ───────────────────────────────────────────────────
    carrier_locked = Column(Boolean)
    symbol_locked = Column(Boolean)
    recording_started = Column(DateTime(timezone=True))
    recording_stopped = Column(DateTime(timezone=True))
    data_volume_bytes = Column(Float)
    frame_count = Column(Integer)
    average_ebno = Column(Float)
    tracking_error_summary = Column(JSONB)  # {max_az, max_el, mean_az, mean_el}

    # ── Time sync state at pass time ─────────────────────────────────────────
    time_source = Column(String(100))       # GPS, NTP, IRIG
    clock_offset_ms = Column(Float)

    # ── Environment ──────────────────────────────────────────────────────────
    weather_summary = Column(JSONB)         # {wind_speed, temperature, humidity}

    # ── Cryptographic attestation ────────────────────────────────────────────
    pass_report_hash = Column(String(128))        # SHA-256 of MCS pass report
    artifact_manifest_hash = Column(String(128))  # SHA-256 of artifact manifest
    agent_signature = Column(Text)                # optional Ed25519/RSA signature
    signature_algorithm = Column(String(50))      # e.g. ed25519, rsa-sha256

    # ── Legacy / generic fields ──────────────────────────────────────────────
    received_bytes = Column(Float)
    recorded_file_url = Column(String(1024))
    signal_quality = Column(JSONB)
    notes = Column(Text)
    received_at = Column(DateTime(timezone=True), server_default=func.now())

class StationReadinessEvent(Base):
    """Engineer's manual readiness confirmation for a job.
    Mandatory gate before EXECUTING: the cloud can never auto-execute against
    expensive hardware unless the profile operation_mode is AUTOMATIC.
    Extended statuses support safety interlocks and weather holds."""
    __tablename__ = 'station_readiness_events'
    __table_args__ = (
        Index('idx_readiness_job', 'job_id', 'confirmed_at'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('observation_jobs.id'), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey('ground_stations.id'))
    profile_id = Column(UUID(as_uuid=True), ForeignKey('station_operation_profiles.id'))
    engineer_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    confirmed_at = Column(DateTime(timezone=True), server_default=func.now())
    checklist_results = Column(JSONB)     # e.g. {"mcs_profile_loaded": true, "weather_safe": true, ...}
    # READY, NOT_READY, BLOCKED, SAFETY_STOP, EQUIPMENT_FAULT, WEATHER_HOLD
    status = Column(String(50), default='NOT_READY')
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())