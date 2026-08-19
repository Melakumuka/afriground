"""phase2_outbox_retry

Revision ID: b5935c0e3f2d
Revises: a59283fc1078
Create Date: 2026-08-19 21:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5935c0e3f2d'
down_revision: Union[str, None] = 'a59283fc1078'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'outbox_events',
        sa.Column('attempt_count', sa.Integer(), server_default='0', nullable=False),
    )
    op.add_column(
        'outbox_events',
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('outbox_events', 'next_retry_at')
    op.drop_column('outbox_events', 'attempt_count')