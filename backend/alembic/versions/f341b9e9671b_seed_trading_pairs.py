"""Seed default trading pairs for BitNova Exchange."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f341b9e9671b"
down_revision: Union[str, Sequence[str], None] = "b6c8fb3eaac7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_PAIRS = [
    ("BTC", "USDT", "BTCUSDT", "BTC/USDT", 2, 8, "0.01", "0.00000001", "0.0001", None, "10"),
    ("ETH", "USDT", "ETHUSDT", "ETH/USDT", 2, 8, "0.01", "0.00000001", "0.0010", None, "10"),
    ("BNB", "USDT", "BNBUSDT", "BNB/USDT", 2, 8, "0.01", "0.00000001", "0.0100", None, "10"),
    ("SOL", "USDT", "SOLUSDT", "SOL/USDT", 2, 8, "0.01", "0.00000001", "0.0100", None, "10"),
    ("XRP", "USDT", "XRPUSDT", "XRP/USDT", 4, 8, "0.0001", "0.00000001", "1.0000", None, "10"),
]


def upgrade() -> None:
    connection = op.get_bind()

    assets = {
        row.symbol: row.id
        for row in connection.execute(
            sa.text("SELECT id, symbol FROM assets")
        )
    }

    for (
        base_symbol,
        quote_symbol,
        pair_code,
        display_name,
        price_precision,
        quantity_precision,
        tick_size,
        step_size,
        min_qty,
        max_qty,
        min_value,
    ) in DEFAULT_PAIRS:

        if base_symbol not in assets:
            raise RuntimeError(f"Missing asset: {base_symbol}")

        if quote_symbol not in assets:
            raise RuntimeError(f"Missing asset: {quote_symbol}")

        connection.execute(
            sa.text(
                """
                INSERT INTO trading_pairs (
                    id,
                    base_asset_id,
                    quote_asset_id,
                    pair_code,
                    display_name,
                    price_precision,
                    quantity_precision,
                    tick_size,
                    step_size,
                    min_order_quantity,
                    max_order_quantity,
                    min_order_value,
                    status,
                    is_visible,
                    is_default
                )
                VALUES (
                    gen_random_uuid(),
                    :base_asset_id,
                    :quote_asset_id,
                    :pair_code,
                    :display_name,
                    :price_precision,
                    :quantity_precision,
                    :tick_size,
                    :step_size,
                    :min_qty,
                    :max_qty,
                    :min_value,
                    'ACTIVE',
                    TRUE,
                    :is_default
                )
                ON CONFLICT (pair_code) DO NOTHING;
                """
            ),
            {
                "base_asset_id": assets[base_symbol],
                "quote_asset_id": assets[quote_symbol],
                "pair_code": pair_code,
                "display_name": display_name,
                "price_precision": price_precision,
                "quantity_precision": quantity_precision,
                "tick_size": tick_size,
                "step_size": step_size,
                "min_qty": min_qty,
                "max_qty": max_qty,
                "min_value": min_value,
                "is_default": pair_code == "BTCUSDT",
            },
        )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            DELETE FROM trading_pairs
            WHERE pair_code IN (
                'BTCUSDT',
                'ETHUSDT',
                'BNBUSDT',
                'SOLUSDT',
                'XRPUSDT'
            );
            """
        )
    )