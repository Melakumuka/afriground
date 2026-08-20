"""phase42_support_ticket_columns

Adds reporter_id and category to support_tickets (Phase 4.2).

Revision ID: f1a2b3c4d5e6
Revises: e7f8a9b0c1d2
Create Date: 2026-08-20 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'e7f8a9b0c1d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'support_tickets',
        sa.Column('reporter_id', sa.UUID(), sa.ForeignKey('users.id'), nullable=True),
    )
    op.add_column(
        'support_tickets',
        sa.Column('category', sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('support_tickets', 'category')
    op.drop_column('support_tickets', 'reporter_id')