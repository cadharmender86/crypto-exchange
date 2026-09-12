"""create_orders_table

Revision ID: 36013415874d
Revises: 3a5e867e6142
Create Date: 2026-09-12 12:52:19.313059

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '36013415874d'
down_revision: Union[str, Sequence[str], None] = 'f341b9e9671b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------
    # ENUMS
    # -------------------------------------------------------
    order_side = postgresql.ENUM(
        "BUY",
        "SELL",
        name="order_side_enum",
        create_type=False,
    )

    order_status = postgresql.ENUM(
        "NEW",
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELLED",
        "EXPIRED",
        "REJECTED",
        name="order_status_enum",
        create_type=False,
    )

    order_side.create(op.get_bind(), checkfirst=True)
    order_status.create(op.get_bind(), checkfirst=True)

    # -------------------------------------------------------
    # CREATE ORDERS TABLE
    # -------------------------------------------------------
    op.create_table(
        "orders",

        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),

        sa.Column(
            "base_asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assets.id"),
            nullable=False,
        ),

        sa.Column(
            "quote_asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assets.id"),
            nullable=False,
        ),

        sa.Column(
            "side",
            order_side,
            nullable=False,
        ),

        sa.Column(
            "price",
            sa.Numeric(24, 8),
            nullable=False,
        ),

        sa.Column(
            "quantity",
            sa.Numeric(24, 8),
            nullable=False,
        ),

        sa.Column(
            "status",
            order_status,
            nullable=False,
            server_default="NEW",
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # -------------------------------------------------------
    # INDEXES
    # -------------------------------------------------------
    op.create_index(
        "ix_orders_user_id",
        "orders",
        ["user_id"],
    )

    op.create_index(
        "ix_orders_base_asset_id",
        "orders",
        ["base_asset_id"],
    )

    op.create_index(
        "ix_orders_quote_asset_id",
        "orders",
        ["quote_asset_id"],
    )

    op.create_index(
        "ix_orders_status",
        "orders",
        ["status"],
    )

    op.create_index(
        "ix_orders_created_at",
        "orders",
        ["created_at"],
    )


def downgrade() -> None:

    op.drop_index("ix_orders_created_at", table_name="orders")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_quote_asset_id", table_name="orders")
    op.drop_index("ix_orders_base_asset_id", table_name="orders")
    op.drop_index("ix_orders_user_id", table_name="orders")

    op.drop_table("orders")

    order_status.drop(op.get_bind(), checkfirst=True)
    order_side.drop(op.get_bind(), checkfirst=True)