"""phase2_edge_telemetry

Revision ID: a4f7c9d1e2b3
Revises: b5935c0e3f2d
Create Date: 2026-08-19 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a4f7c9d1e2b3'
down_revision: Union[str, None] = 'b5935c0e3f2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'datasets',
        sa.Column('observation_job_id', sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        'fk_datasets_observation_job',
        'datasets', 'observation_jobs',
        ['observation_job_id'], ['id'],
    )
    op.create_table(
        'station_heartbeats',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('station_id', sa.UUID(), nullable=False),
        sa.Column('agent_id', sa.String(length=255), nullable=False),
        sa.Column('agent_version', sa.String(length=100), nullable=True),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['station_id'], ['ground_stations.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'station_telemetry_readings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('station_id', sa.UUID(), nullable=False),
        sa.Column('agent_id', sa.String(length=255), nullable=False),
        sa.Column('telemetry_type', sa.String(length=50), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['station_id'], ['ground_stations.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_station_telemetry_readings_station_type',
        'station_telemetry_readings',
        ['station_id', 'telemetry_type', 'recorded_at'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_station_telemetry_readings_station_type', table_name='station_telemetry_readings')
    op.drop_table('station_telemetry_readings')
    op.drop_table('station_heartbeats')
    op.drop_constraint('fk_datasets_observation_job', 'datasets', type_='foreignkey')
    op.drop_column('datasets', 'observation_job_id')