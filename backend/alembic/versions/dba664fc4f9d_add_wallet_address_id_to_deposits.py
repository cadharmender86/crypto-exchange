"""add wallet_address_id to deposits

Revision ID: dba664fc4f9d
Revises: 6a209c39f2a3
Create Date: 2026-09-06 15:35:26.727452

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'dba664fc4f9d'
down_revision: Union[str, Sequence[str], None] = '6a209c39f2a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.add_column(
        "deposits",
        sa.Column(
            "wallet_address_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_deposits_wallet_address_id",
        "deposits",
        ["wallet_address_id"],
    )

    op.create_foreign_key(
        "fk_deposits_wallet_address_id",
        "deposits",
        "wallet_addresses",
        ["wallet_address_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade():

    op.drop_constraint(
        "fk_deposits_wallet_address_id",
        "deposits",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_deposits_wallet_address_id",
        table_name="deposits",
    )

    op.drop_column("deposits", "wallet_address_id")