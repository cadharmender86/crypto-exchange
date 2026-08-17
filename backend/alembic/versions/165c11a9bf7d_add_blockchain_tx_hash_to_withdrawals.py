"""add blockchain tx hash to withdrawals

Revision ID: 165c11a9bf7d
Revises: 2d91fa12bdd5
Create Date: 2026-08-18 03:27:57.587366

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "165c11a9bf7d"
down_revision: Union[str, Sequence[str], None] = "2d91fa12bdd5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.add_column(
        "withdrawals",
        sa.Column(
            "blockchain_tx_hash",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_withdrawals_blockchain_tx_hash",
        "withdrawals",
        ["blockchain_tx_hash"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index(
        "ix_withdrawals_blockchain_tx_hash",
        table_name="withdrawals",
    )

    op.drop_column(
        "withdrawals",
        "blockchain_tx_hash",
    )