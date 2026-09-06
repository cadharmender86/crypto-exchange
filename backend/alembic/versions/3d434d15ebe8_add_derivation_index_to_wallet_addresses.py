"""add derivation index to wallet addresses

Revision ID: 3d434d15ebe8
Revises: dba664fc4f9d
Create Date: 2026-09-06 20:56:33.952326

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d434d15ebe8'
down_revision: Union[str, Sequence[str], None] = 'dba664fc4f9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "wallet_addresses",
        sa.Column("derivation_index", sa.Integer(), nullable=True),
    )

    op.create_index(
        "ix_wallet_addresses_derivation_index",
        "wallet_addresses",
        ["derivation_index"],
    )


def downgrade():
    op.drop_index(
        "ix_wallet_addresses_derivation_index",
        table_name="wallet_addresses",
    )

    op.drop_column(
        "wallet_addresses",
        "derivation_index",
    )