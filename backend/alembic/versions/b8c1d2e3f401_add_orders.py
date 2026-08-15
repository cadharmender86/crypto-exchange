"""add orders table

Revision ID: b8c1d2e3f401
Revises: 7a1c2d9e4f10
Create Date: 2026-08-16

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b8c1d2e3f401"
down_revision: Union[str, Sequence[str], None] = "7a1c2d9e4f10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("base_asset_id", sa.UUID(), nullable=False),
        sa.Column("quote_asset_id", sa.UUID(), nullable=False),
        sa.Column("client_order_id", sa.String(length=100), nullable=True),
        sa.Column("side", sa.String(length=4), nullable=False),
        sa.Column("order_type", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("price", sa.Numeric(precision=38, scale=18), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=38, scale=18), nullable=False),
        sa.Column("filled_quantity", sa.Numeric(precision=38, scale=18), nullable=False),
        sa.Column("remaining_quantity", sa.Numeric(precision=38, scale=18), nullable=False),
        sa.Column("average_execution_price", sa.Numeric(precision=38, scale=18), nullable=True),
        sa.Column("fee_amount", sa.Numeric(precision=38, scale=18), nullable=False),
        sa.Column("fee_asset_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["base_asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["quote_asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["fee_asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "client_order_id", name="uq_orders_user_client_order_id"),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_index("ix_orders_base_asset_id", "orders", ["base_asset_id"])
    op.create_index("ix_orders_quote_asset_id", "orders", ["quote_asset_id"])
    op.create_index("ix_orders_fee_asset_id", "orders", ["fee_asset_id"])
    op.create_index("ix_orders_side", "orders", ["side"])
    op.create_index("ix_orders_order_type", "orders", ["order_type"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_created_at", "orders", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_orders_created_at", table_name="orders")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_order_type", table_name="orders")
    op.drop_index("ix_orders_side", table_name="orders")
    op.drop_index("ix_orders_fee_asset_id", table_name="orders")
    op.drop_index("ix_orders_quote_asset_id", table_name="orders")
    op.drop_index("ix_orders_base_asset_id", table_name="orders")
    op.drop_index("ix_orders_user_id", table_name="orders")
    op.drop_table("orders")
