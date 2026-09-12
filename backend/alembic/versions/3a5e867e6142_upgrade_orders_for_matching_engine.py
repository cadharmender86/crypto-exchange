"""upgrade_orders_for_matching_engine

Revision ID: 3a5e867e6142
Revises: f341b9e9671b
Create Date: 2026-09-12 12:26:58.644862

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3a5e867e6142'
down_revision: Union[str, Sequence[str], None] = '36013415874d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    order_side = postgresql.ENUM(
        "BUY",
        "SELL",
        name="order_side_enum",
    )

    order_type = postgresql.ENUM(
        "LIMIT",
        "MARKET",
        "STOP_LIMIT",
        "STOP_MARKET",
        name="order_type_enum",
    )

    time_in_force = postgresql.ENUM(
        "GTC",
        "IOC",
        "FOK",
        name="time_in_force_enum",
    )

    order_status = postgresql.ENUM(
        "NEW",
        "PARTIALLY_FILLED",
        "FILLED",
        "CANCELLED",
        "EXPIRED",
        "REJECTED",
        name="order_status_enum",
    )

    order_side.create(op.get_bind(), checkfirst=True)
    order_type.create(op.get_bind(), checkfirst=True)
    time_in_force.create(op.get_bind(), checkfirst=True)
    order_status.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "orders",
        sa.Column(
            "trading_pair_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "order_type",
            sa.Enum(name="order_type_enum"),
            nullable=False,
            server_default="LIMIT",
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "time_in_force",
            sa.Enum(name="time_in_force_enum"),
            nullable=False,
            server_default="GTC",
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "average_price",
            sa.Numeric(24, 8),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "quote_amount",
            sa.Numeric(24, 8),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "executed_quantity",
            sa.Numeric(24, 8),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "remaining_quantity",
            sa.Numeric(24, 8),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "fee_asset_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "fee_amount",
            sa.Numeric(24, 8),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "cancel_reason",
            sa.String(length=100),
            nullable=True,
        ),
    )

    # Populate trading_pair_id for existing orders
    op.execute("""
        UPDATE orders
        SET trading_pair_id = tp.id
        FROM trading_pairs tp
        WHERE orders.base_asset_id = tp.base_asset_id
        AND orders.quote_asset_id = tp.quote_asset_id;
    """)

    op.execute("""
        UPDATE orders
        SET remaining_quantity = quantity
        WHERE remaining_quantity = 0;
    """)

    op.create_foreign_key(
        "fk_orders_trading_pair",
        "orders",
        "trading_pairs",
        ["trading_pair_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_orders_fee_asset",
        "orders",
        "assets",
        ["fee_asset_id"],
        ["id"],
    )

    op.alter_column(
        "orders",
        "trading_pair_id",
        nullable=False,
    )

    op.create_index(
        "idx_order_book_lookup",
        "orders",
        [
            "trading_pair_id",
            "side",
            "status",
            "price",
            "created_at",
        ],
    )

    op.create_index(
        "idx_order_user_status",
        "orders",
        [
            "user_id",
            "status",
        ],
    )

    op.drop_constraint(
        "orders_base_asset_id_fkey",
        "orders",
        type_="foreignkey",
    )

    op.drop_constraint(
        "orders_quote_asset_id_fkey",
        "orders",
        type_="foreignkey",
    )

    op.drop_column("orders", "base_asset_id")
    op.drop_column("orders", "quote_asset_id")

def downgrade():

    op.add_column(
        "orders",
        sa.Column(
            "base_asset_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "quote_asset_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.drop_index("idx_order_book_lookup")
    op.drop_index("idx_order_user_status")

    op.drop_constraint("fk_orders_trading_pair", "orders", type_="foreignkey")
    op.drop_constraint("fk_orders_fee_asset", "orders", type_="foreignkey")

    op.drop_column("orders", "trading_pair_id")
    op.drop_column("orders", "order_type")
    op.drop_column("orders", "time_in_force")
    op.drop_column("orders", "average_price")
    op.drop_column("orders", "quote_amount")
    op.drop_column("orders", "executed_quantity")
    op.drop_column("orders", "remaining_quantity")
    op.drop_column("orders", "fee_asset_id")
    op.drop_column("orders", "fee_amount")
    op.drop_column("orders", "cancel_reason")

    postgresql.ENUM(name="order_side_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="order_type_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="time_in_force_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="order_status_enum").drop(op.get_bind(), checkfirst=True)