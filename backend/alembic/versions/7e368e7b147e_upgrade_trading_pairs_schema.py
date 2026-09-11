from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "7e368e7b147e"
down_revision = "3fcd1f1dac8d"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Rename columns
    op.alter_column(
        "trading_pairs",
        "minimum_order_quantity",
        new_column_name="min_order_quantity",
    )

    op.alter_column(
        "trading_pairs",
        "maximum_order_quantity",
        new_column_name="max_order_quantity",
    )

    op.alter_column(
        "trading_pairs",
        "minimum_order_value",
        new_column_name="min_order_value",
    )

    # 2. Change default quantity precision
    op.alter_column(
        "trading_pairs",
        "quantity_precision",
        existing_type=sa.Integer(),
        server_default="8",
    )

    # 3. Add timestamps
    op.add_column(
        "trading_pairs",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.add_column(
        "trading_pairs",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # 4. Create missing indexes
    op.create_index(
        "idx_trading_pairs_visible",
        "trading_pairs",
        ["is_visible"],
    )

    op.create_index(
        "idx_trading_pairs_default",
        "trading_pairs",
        ["is_default"],
    )


def downgrade():
    op.drop_index(
        "idx_trading_pairs_default",
        table_name="trading_pairs",
    )

    op.drop_index(
        "idx_trading_pairs_visible",
        table_name="trading_pairs",
    )

    op.drop_column("trading_pairs", "updated_at")
    op.drop_column("trading_pairs", "created_at")

    op.alter_column(
        "trading_pairs",
        "min_order_quantity",
        new_column_name="minimum_order_quantity",
    )

    op.alter_column(
        "trading_pairs",
        "max_order_quantity",
        new_column_name="maximum_order_quantity",
    )

    op.alter_column(
        "trading_pairs",
        "min_order_value",
        new_column_name="minimum_order_value",
    )

    op.alter_column(
        "trading_pairs",
        "quantity_precision",
        existing_type=sa.Integer(),
        server_default="6",
    )