"""phase3_sla_webhooks_routing

Adds SLA violation records (Phase 3.0), per-org webhook delivery tracking
(Phase 3.1), and no schema changes for network routing (Phase 3.2 — computed
from existing StationQualityScore / StationRiskScore / certification).

Revision ID: c5d6e7f8a9b0
Revises: a4f7c9d1e2b3
Create Date: 2026-08-20 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5d6e7f8a9b0'
down_revision: Union[str, None] = 'a4f7c9d1e2b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sla_violations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('mission_id', sa.UUID(), nullable=False),
        sa.Column('observation_job_id', sa.UUID(), nullable=False),
        sa.Column('sla_type', sa.String(length=50), nullable=False),
        sa.Column('target_value', sa.Float(), nullable=False),
        sa.Column('actual_value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='open', nullable=False),
        sa.Column('violated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['mission_id'], ['missions.id']),
        sa.ForeignKeyConstraint(['observation_job_id'], ['observation_jobs.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_sla_violations_mission_status',
        'sla_violations',
        ['mission_id', 'status', 'violated_at'],
        unique=False,
    )
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('webhook_id', sa.UUID(), nullable=False),
        sa.Column('outbox_event_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['outbox_event_id'], ['outbox_events.id']),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhooks.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('webhook_id', 'outbox_event_id', name='uq_webhook_delivery'),
    )


def downgrade() -> None:
    op.drop_table('webhook_deliveries')
    op.drop_index('ix_sla_violations_mission_status', table_name='sla_violations')
    op.drop_table('sla_violations')
