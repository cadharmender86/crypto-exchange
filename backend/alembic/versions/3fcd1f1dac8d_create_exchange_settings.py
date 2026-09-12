"""create exchange settings

Revision ID: 3fcd1f1dac8d
Revises: 20260910_create_trading_pairs
Create Date: 2026-09-11 02:26:41.919660

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision: str = '3fcd1f1dac8d'
down_revision: Union[str, Sequence[str], None] = '20260910_create_trading_pairs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "exchange_settings",

        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "key",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "value",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "value_type",
            sa.String(length=30),
            nullable=False,
            server_default="string",
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "is_public",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
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

        sa.UniqueConstraint("key", name="uq_exchange_settings_key"),
    )

    op.create_index(
        "ix_exchange_settings_key",
        "exchange_settings",
        ["key"],
        unique=True,
    )

    exchange_settings = sa.table(
        "exchange_settings",

        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("key", sa.String),
        sa.column("value", sa.Text),
        sa.column("value_type", sa.String),
        sa.column("description", sa.Text),
        sa.column("is_public", sa.Boolean),
    )

    op.bulk_insert(
        exchange_settings,
        [
            {
                "id": uuid.uuid4(),
                "key": "maintenance_mode",
                "value": "false",
                "value_type": "boolean",
                "description": "Enable exchange maintenance mode.",
                "is_public": False,
            },
            {
                "id": uuid.uuid4(),
                "key": "spot_trading_enabled",
                "value": "true",
                "value_type": "boolean",
                "description": "Enable or disable spot trading.",
                "is_public": False,
            },
            {
                "id": uuid.uuid4(),
                "key": "margin_trading_enabled",
                "value": "false",
                "value_type": "boolean",
                "description": "Enable or disable margin trading.",
                "is_public": False,
            },
            {
                "id": uuid.uuid4(),
                "key": "withdrawals_enabled",
                "value": "false",
                "value_type": "boolean",
                "description": "Enable crypto withdrawals.",
                "is_public": False,
            },
            {
                "id": uuid.uuid4(),
                "key": "deposits_enabled",
                "value": "false",
                "value_type": "boolean",
                "description": "Enable crypto deposits.",
                "is_public": False,
            },
            {
                "id": uuid.uuid4(),
                "key": "default_market",
                "value": "BTCUSDT",
                "value_type": "string",
                "description": "Default market pair shown on home screen.",
                "is_public": True,
            },
            {
                "id": uuid.uuid4(),
                "key": "usdt_inr_rate",
                "value": "87.10",
                "value_type": "decimal",
                "description": "Fallback USDT to INR conversion rate.",
                "is_public": True,
            },
            {
                "id": uuid.uuid4(),
                "key": "market_cache_ttl",
                "value": "30",
                "value_type": "integer",
                "description": "Redis cache TTL in seconds.",
                "is_public": False,
            },
            {
                "id": uuid.uuid4(),
                "key": "kyc_required_for_withdrawal",
                "value": "true",
                "value_type": "boolean",
                "description": "Require approved KYC before withdrawals.",
                "is_public": False,
            },
            {
                "id": uuid.uuid4(),
                "key": "referral_enabled",
                "value": "true",
                "value_type": "boolean",
                "description": "Enable referral reward system.",
                "is_public": False,
            },
        ],
    )


def downgrade() -> None:

    op.drop_index("ix_exchange_settings_key", table_name="exchange_settings")
    op.drop_table("exchange_settings")