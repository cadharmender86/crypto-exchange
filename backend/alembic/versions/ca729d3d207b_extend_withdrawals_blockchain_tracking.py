"""extend withdrawals blockchain tracking

Revision ID: ca729d3d207b
Revises: 0eab2babd0cd
Create Date: 2026-09-12 18:27:49.847885

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca729d3d207b'
down_revision: Union[str, Sequence[str], None] = '0eab2babd0cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "withdrawals",
        sa.Column("blockchain_tx_hash", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "withdrawals",
        sa.Column("confirmations", sa.Integer(), nullable=False, server_default="0"),
    )

    op.add_column(
        "withdrawals",
        sa.Column("failure_reason", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "withdrawals",
        sa.Column("broadcasted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Remove temporary default after existing rows are updated.
    op.alter_column("withdrawals", "confirmations", server_default=None)


def downgrade():
    op.drop_column("withdrawals", "broadcasted_at")
    op.drop_column("withdrawals", "failure_reason")
    op.drop_column("withdrawals", "confirmations")
    op.drop_column("withdrawals", "blockchain_tx_hash")