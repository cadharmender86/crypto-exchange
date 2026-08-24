"""add buyer seller user ids to trades"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision = "93c703e8b6f2"
down_revision = "2b97bf838e8d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "trades",
        sa.Column("buyer_user_id", sa.UUID(), nullable=True),
    )

    op.add_column(
        "trades",
        sa.Column("seller_user_id", sa.UUID(), nullable=True),
    )

    op.create_index(
        "ix_trades_buyer_user_id",
        "trades",
        ["buyer_user_id"],
        unique=False,
    )

    op.create_index(
        "ix_trades_seller_user_id",
        "trades",
        ["seller_user_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_trades_buyer_user_id",
        "trades",
        "users",
        ["buyer_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        "fk_trades_seller_user_id",
        "trades",
        "users",
        ["seller_user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_trades_buyer_user_id", "trades", type_="foreignkey")
    op.drop_constraint("fk_trades_seller_user_id", "trades", type_="foreignkey")

    op.drop_index("ix_trades_buyer_user_id", table_name="trades")
    op.drop_index("ix_trades_seller_user_id", table_name="trades")

    op.drop_column("trades", "buyer_user_id")
    op.drop_column("trades", "seller_user_id")