"""Station Gateway models upgrade — StationOperationProfile, ExecutionReceipt, StationReadinessEvent

Adds structured PFM730-ready fields to support the Station-Led Configuration
architecture (configure-once, execute-many).

Revision ID: g8h9i0j1k2l3
Revises: f1a2b3c4d5e6
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = 'g8h9i0j1k2l3'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── StationOperationProfile: add new columns ─────────────────────────────
    op.add_column('station_operation_profiles',
                  sa.Column('satellite_id', sa.dialects.postgresql.UUID(as_uuid=True),
                            sa.ForeignKey('spacecraft.id'), nullable=True))
    op.add_column('station_operation_profiles',
                  sa.Column('certification_state', sa.String(50), server_default='CONFIGURING'))
    op.add_column('station_operation_profiles',
                  sa.Column('certified_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('station_operation_profiles',
                  sa.Column('certified_by', sa.dialects.postgresql.UUID(as_uuid=True),
                            sa.ForeignKey('users.id'), nullable=True))
    op.add_column('station_operation_profiles',
                  sa.Column('qualification_job_id', sa.dialects.postgresql.UUID(as_uuid=True),
                            sa.ForeignKey('observation_jobs.id'), nullable=True))
    op.add_column('station_operation_profiles',
                  sa.Column('operation_mode', sa.String(50), server_default='MANUAL_CONFIRMED'))
    op.add_column('station_operation_profiles',
                  sa.Column('acu_config_payload', JSONB, nullable=True))
    op.add_column('station_operation_profiles',
                  sa.Column('rf_path_payload', JSONB, nullable=True))
    op.add_column('station_operation_profiles',
                  sa.Column('decoder_config_payload', JSONB, nullable=True))
    op.add_column('station_operation_profiles',
                  sa.Column('safety_payload', JSONB, nullable=True))
    op.add_column('station_operation_profiles',
                  sa.Column('total_passes', sa.Integer(), server_default='0'))
    op.add_column('station_operation_profiles',
                  sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True))

    # ── ExecutionReceipt: add structured PFM730 telemetry fields ─────────────
    op.add_column('execution_receipts',
                  sa.Column('station_id', sa.dialects.postgresql.UUID(as_uuid=True),
                            sa.ForeignKey('ground_stations.id'), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('profile_id', sa.dialects.postgresql.UUID(as_uuid=True),
                            sa.ForeignKey('station_operation_profiles.id'), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('receipt_version', sa.String(20), server_default='1.0'))
    op.add_column('execution_receipts',
                  sa.Column('carrier_locked', sa.Boolean(), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('symbol_locked', sa.Boolean(), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('recording_started', sa.DateTime(timezone=True), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('recording_stopped', sa.DateTime(timezone=True), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('data_volume_bytes', sa.Float(), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('frame_count', sa.Integer(), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('average_ebno', sa.Float(), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('tracking_error_summary', JSONB, nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('time_source', sa.String(100), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('clock_offset_ms', sa.Float(), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('weather_summary', JSONB, nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('pass_report_hash', sa.String(128), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('artifact_manifest_hash', sa.String(128), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('agent_signature', sa.Text(), nullable=True))
    op.add_column('execution_receipts',
                  sa.Column('signature_algorithm', sa.String(50), nullable=True))

    # ── StationReadinessEvent: add station/profile context and notes ─────────
    op.add_column('station_readiness_events',
                  sa.Column('station_id', sa.dialects.postgresql.UUID(as_uuid=True),
                            sa.ForeignKey('ground_stations.id'), nullable=True))
    op.add_column('station_readiness_events',
                  sa.Column('profile_id', sa.dialects.postgresql.UUID(as_uuid=True),
                            sa.ForeignKey('station_operation_profiles.id'), nullable=True))
    op.add_column('station_readiness_events',
                  sa.Column('notes', sa.Text(), nullable=True))


def downgrade() -> None:
    # ── StationReadinessEvent ────────────────────────────────────────────────
    op.drop_column('station_readiness_events', 'notes')
    op.drop_column('station_readiness_events', 'profile_id')
    op.drop_column('station_readiness_events', 'station_id')

    # ── ExecutionReceipt ─────────────────────────────────────────────────────
    op.drop_column('execution_receipts', 'signature_algorithm')
    op.drop_column('execution_receipts', 'agent_signature')
    op.drop_column('execution_receipts', 'artifact_manifest_hash')
    op.drop_column('execution_receipts', 'pass_report_hash')
    op.drop_column('execution_receipts', 'weather_summary')
    op.drop_column('execution_receipts', 'clock_offset_ms')
    op.drop_column('execution_receipts', 'time_source')
    op.drop_column('execution_receipts', 'tracking_error_summary')
    op.drop_column('execution_receipts', 'average_ebno')
    op.drop_column('execution_receipts', 'frame_count')
    op.drop_column('execution_receipts', 'data_volume_bytes')
    op.drop_column('execution_receipts', 'recording_stopped')
    op.drop_column('execution_receipts', 'recording_started')
    op.drop_column('execution_receipts', 'symbol_locked')
    op.drop_column('execution_receipts', 'carrier_locked')
    op.drop_column('execution_receipts', 'receipt_version')
    op.drop_column('execution_receipts', 'profile_id')
    op.drop_column('execution_receipts', 'station_id')

    # ── StationOperationProfile ──────────────────────────────────────────────
    op.drop_column('station_operation_profiles', 'last_used_at')
    op.drop_column('station_operation_profiles', 'total_passes')
    op.drop_column('station_operation_profiles', 'safety_payload')
    op.drop_column('station_operation_profiles', 'decoder_config_payload')
    op.drop_column('station_operation_profiles', 'rf_path_payload')
    op.drop_column('station_operation_profiles', 'acu_config_payload')
    op.drop_column('station_operation_profiles', 'operation_mode')
    op.drop_column('station_operation_profiles', 'qualification_job_id')
    op.drop_column('station_operation_profiles', 'certified_by')
    op.drop_column('station_operation_profiles', 'certified_at')
    op.drop_column('station_operation_profiles', 'certification_state')
    op.drop_column('station_operation_profiles', 'satellite_id')
