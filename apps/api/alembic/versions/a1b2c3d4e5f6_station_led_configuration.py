"""station_led_configuration

Adds StationOperationProfile + StationReadinessEvent (Station-Led Configuration
& Local Gateway) and wires ObservationJob to the operation profile with a
readiness_status gate column.

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-08-21 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'station_operation_profiles',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('station_id', sa.UUID(), sa.ForeignKey('ground_stations.id'), nullable=False),
        sa.Column('mission_profile_id', sa.UUID(), sa.ForeignKey('mission_profiles.id'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='CONFIGURING'),
        sa.Column('mcs_profile_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('hdr_config_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'station_readiness_events',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('job_id', sa.UUID(), sa.ForeignKey('observation_jobs.id'), nullable=False),
        sa.Column('engineer_id', sa.UUID(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('checklist_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='NOT_READY'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_readiness_job', 'station_readiness_events', ['job_id', 'confirmed_at'])
    op.add_column(
        'observation_jobs',
        sa.Column('station_operation_profile_id', sa.UUID(), sa.ForeignKey('station_operation_profiles.id'), nullable=True),
    )
    op.add_column(
        'observation_jobs',
        sa.Column('readiness_status', sa.String(length=50), nullable=False, server_default='PENDING'),
    )
    op.create_index('idx_jobs_readiness', 'observation_jobs', ['readiness_status'])


def downgrade() -> None:
    op.drop_index('idx_jobs_readiness', table_name='observation_jobs')
    op.drop_column('observation_jobs', 'readiness_status')
    op.drop_column('observation_jobs', 'station_operation_profile_id')
    op.drop_index('idx_readiness_job', table_name='station_readiness_events')
    op.drop_table('station_readiness_events')
    op.drop_table('station_operation_profiles')