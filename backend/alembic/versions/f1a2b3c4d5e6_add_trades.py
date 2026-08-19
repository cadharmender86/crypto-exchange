"""add executed trades table

Revision ID: f1a2b3c4d5e6
Revises: eca6531ff399
Create Date: 2026-08-20

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "eca6531ff399"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "trades",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("buy_order_id", sa.UUID(), nullable=False),
        sa.Column("sell_order_id", sa.UUID(), nullable=False),
        sa.Column("base_asset_id", sa.UUID(), nullable=False),
        sa.Column("quote_asset_id", sa.UUID(), nullable=False),
        sa.Column("price", sa.Numeric(38, 18), nullable=False),
        sa.Column("quantity", sa.Numeric(38, 18), nullable=False),
        sa.Column("quote_amount", sa.Numeric(38, 18), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["base_asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["quote_asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trades_buy_order_id", "trades", ["buy_order_id"], unique=False)
    op.create_index("ix_trades_sell_order_id", "trades", ["sell_order_id"], unique=False)
    op.create_index("ix_trades_base_asset_id", "trades", ["base_asset_id"], unique=False)
    op.create_index("ix_trades_quote_asset_id", "trades", ["quote_asset_id"], unique=False)
    op.create_index("ix_trades_created_at", "trades", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_trades_created_at", table_name="trades")
    op.drop_index("ix_trades_quote_asset_id", table_name="trades")
    op.drop_index("ix_trades_base_asset_id", table_name="trades")
    op.drop_index("ix_trades_sell_order_id", table_name="trades")
    op.drop_index("ix_trades_buy_order_id", table_name="trades")
    op.drop_table("trades")
