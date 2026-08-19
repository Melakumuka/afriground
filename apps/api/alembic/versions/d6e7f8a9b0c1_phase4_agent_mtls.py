"""phase4_agent_mtls

Adds certificate validity/revocation tracking to station agent identities
(Phase 4.0 — mTLS edge agent bridge).

Revision ID: d6e7f8a9b0c1
Revises: c5d6e7f8a9b0
Create Date: 2026-08-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6e7f8a9b0c1'
down_revision: Union[str, None] = 'c5d6e7f8a9b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'station_agent_identities',
        sa.Column('certificate_valid_until', sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        'station_agent_identities',
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('station_agent_identities', 'revoked_at')
    op.drop_column('station_agent_identities', 'certificate_valid_until')