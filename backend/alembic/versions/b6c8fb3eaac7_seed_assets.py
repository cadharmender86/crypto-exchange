"""Seed default assets for BitNova Exchange."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b6c8fb3eaac7"
down_revision: Union[str, Sequence[str], None] = "7e368e7b147e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            INSERT INTO assets (
                id,
                symbol,
                name,
                asset_type,
                deposit_enabled,
                withdrawal_enabled,
                trading_enabled,
                decimal_places,
                is_active
            )
            VALUES
                (gen_random_uuid(), 'BTC',  'Bitcoin',        'CRYPTO', TRUE, TRUE, TRUE, 8,  TRUE),
                (gen_random_uuid(), 'ETH',  'Ethereum',       'CRYPTO', TRUE, TRUE, TRUE, 18, TRUE),
                (gen_random_uuid(), 'USDT', 'Tether USD',     'CRYPTO', TRUE, TRUE, TRUE, 6,  TRUE),
                (gen_random_uuid(), 'BNB',  'BNB',            'CRYPTO', TRUE, TRUE, TRUE, 18, TRUE),
                (gen_random_uuid(), 'SOL',  'Solana',         'CRYPTO', TRUE, TRUE, TRUE, 9,  TRUE),
                (gen_random_uuid(), 'XRP',  'Ripple',         'CRYPTO', TRUE, TRUE, TRUE, 6,  TRUE),
                (gen_random_uuid(), 'INR',  'Indian Rupee',   'FIAT',   TRUE, TRUE, TRUE, 2,  TRUE)
            ON CONFLICT (symbol) DO NOTHING;
            """
        )
    )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            DELETE FROM assets
            WHERE symbol IN (
                'BTC',
                'ETH',
                'USDT',
                'BNB',
                'SOL',
                'XRP',
                'INR'
            );
            """
        )
    )