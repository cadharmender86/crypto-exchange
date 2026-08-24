"""add user_id to wallet_addresses"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Replace these with the values generated in your file
revision: str = "4f5651ffe6aa"
down_revision: Union[str, Sequence[str], None] = "3b1ef9a274df"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add column
    op.add_column(
        "wallet_addresses",
        sa.Column("user_id", sa.UUID(), nullable=True),
    )

    # 2. Create index
    op.create_index(
        op.f("ix_wallet_addresses_user_id"),
        "wallet_addresses",
        ["user_id"],
        unique=False,
    )

    # 3. Create foreign key
    op.create_foreign_key(
        "fk_wallet_addresses_user_id",
        "wallet_addresses",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_wallet_addresses_user_id",
        "wallet_addresses",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_wallet_addresses_user_id"),
        table_name="wallet_addresses",
    )

    op.drop_column("wallet_addresses", "user_id")