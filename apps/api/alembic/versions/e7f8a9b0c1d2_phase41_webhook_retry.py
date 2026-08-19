"""phase41_webhook_retry

Adds retry/backoff tracking to per-org webhook deliveries (Phase 4.1).

Revision ID: e7f8a9b0c1d2
Revises: d6e7f8a9b0c1
Create Date: 2026-08-20 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7f8a9b0c1d2'
down_revision: Union[str, None] = 'd6e7f8a9b0c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'webhook_deliveries',
        sa.Column('attempt_count', sa.Integer(), server_default='0', nullable=False),
    )
    op.add_column(
        'webhook_deliveries',
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('webhook_deliveries', 'next_retry_at')
    op.drop_column('webhook_deliveries', 'attempt_count')