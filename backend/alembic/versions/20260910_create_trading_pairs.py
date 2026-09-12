"""create trading_pairs table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260910_create_trading_pairs"
down_revision = "fcc7d7901fff"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "trading_pairs",
        sa.Column(
            "id", 
            postgresql.UUID(as_uuid=True), 
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),   
        sa.Column("base_asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quote_asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pair_code", sa.String(length=20), nullable=False),
        sa.Column("display_name", sa.String(length=30), nullable=False),
        sa.Column("price_precision", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("quantity_precision", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("tick_size", sa.Numeric(24, 12), nullable=False),
        sa.Column("step_size", sa.Numeric(24, 12), nullable=False),
        sa.Column(
            "min_order_quantity",
            sa.Numeric(24, 12),
            nullable=False,
        ),

        sa.Column(
            "max_order_quantity",
            sa.Numeric(24, 12),
            nullable=True,
        ),

        sa.Column(
            "min_order_value",
            sa.Numeric(24, 12),
            nullable=False,
        ),

        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(
            ["base_asset_id"],
            ["assets.id"],
            ondelete="CASCADE",
                ),

        sa.ForeignKeyConstraint(
            ["quote_asset_id"],
            ["assets.id"],
            ondelete="CASCADE",
        ),

        sa.UniqueConstraint("base_asset_id", "quote_asset_id", name="uq_trading_pairs_assets"),
        sa.UniqueConstraint(
            "pair_code",
            name="uq_trading_pairs_pair_code",
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index("idx_trading_pairs_pair_code", "trading_pairs", ["pair_code"])
    op.create_index("idx_trading_pairs_status", "trading_pairs", ["status"])
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

    connection = op.get_bind()

    assets = {
        row.symbol: row.id
        for row in connection.execute(
            sa.text("SELECT id, symbol FROM assets")
        )
    }

    required_assets = {
        "BTC",
        "ETH",
        "SOL",
        "BNB",
        "XRP",
        "USDT",
    }

    missing_assets = required_assets - assets.keys()

    if missing_assets:
        raise RuntimeError(
            f"Missing assets required for trading pair seed: {sorted(missing_assets)}"
        )

    connection.execute(
        sa.text("""
            INSERT INTO trading_pairs (
                id,
                base_asset_id,
                quote_asset_id,
                pair_code,
                display_name,
                status,
                is_visible,
                is_default,
                price_precision,
                quantity_precision,
                tick_size,
                step_size,
                min_order_quantity,
                max_order_quantity,
                min_order_value
            )
            VALUES (
                gen_random_uuid(),
                :base_asset_id,
                :quote_asset_id,
                :pair_code,
                :display_name,
                'ACTIVE',
                true,
                :is_default,
                2,
                8,
                0.01,
                0.00000001,
                0.0001,
                1000000,
                10
            )
        """),
        [
            {
                "base_asset_id": assets["BTC"],
                "quote_asset_id": assets["USDT"],
                "pair_code": "BTCUSDT",
                "display_name": "BTC / USDT",
                "is_default": True,
            },
            {
                "base_asset_id": assets["ETH"],
                "quote_asset_id": assets["USDT"],
                "pair_code": "ETHUSDT",
                "display_name": "ETH / USDT",
                "is_default": False,
            },
            {
                "base_asset_id": assets["SOL"],
                "quote_asset_id": assets["USDT"],
                "pair_code": "SOLUSDT",
                "display_name": "SOL / USDT",
                "is_default": False,
            },
            {
                "base_asset_id": assets["BNB"],
                "quote_asset_id": assets["USDT"],
                "pair_code": "BNBUSDT",
                "display_name": "BNB / USDT",
                "is_default": False,
            },
            {
                "base_asset_id": assets["XRP"],
                "quote_asset_id": assets["USDT"],
                "pair_code": "XRPUSDT",
                "display_name": "XRP / USDT",
                "is_default": False,
            },
        ],
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

    op.drop_index(
        "idx_trading_pairs_status",
        table_name="trading_pairs",
    )

    op.drop_index(
        "idx_trading_pairs_pair_code",
        table_name="trading_pairs",
    )

    op.drop_table("trading_pairs")