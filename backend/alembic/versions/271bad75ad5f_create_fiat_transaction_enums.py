"""create fiat transaction enums"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "271bad75ad5f"
down_revision = "1ee04098d4e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    transaction_type = postgresql.ENUM(
        "INR_DEPOSIT",
        "INR_WITHDRAWAL",
        "TRADE_BUY",
        "TRADE_SELL",
        "WITHDRAWAL_LOCK",
        "WITHDRAWAL_UNLOCK",
        "REFUND",
        "FEE",
        name="fiattransactiontype",
    )

    transaction_status = postgresql.ENUM(
        "PENDING",
        "COMPLETED",
        "FAILED",
        name="fiattransactionstatus",
    )

    transaction_type.create(op.get_bind(), checkfirst=True)
    transaction_status.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        "fiat_transactions",
        "transaction_type",
        existing_type=sa.String(length=50),
        type_=transaction_type,
        postgresql_using="transaction_type::fiattransactiontype",
    )

    op.alter_column(
        "fiat_transactions",
        "status",
        existing_type=sa.String(length=20),
        type_=transaction_status,
        postgresql_using="status::fiattransactionstatus",
    )


def downgrade() -> None:
    op.alter_column(
        "fiat_transactions",
        "transaction_type",
        existing_type=postgresql.ENUM(
            "INR_DEPOSIT",
            "INR_WITHDRAWAL",
            "TRADE_BUY",
            "TRADE_SELL",
            "WITHDRAWAL_LOCK",
            "WITHDRAWAL_UNLOCK",
            "REFUND",
            "FEE",
            name="fiattransactiontype",
        ),
        type_=sa.String(length=50),
        postgresql_using="transaction_type::text",
    )

    op.alter_column(
        "fiat_transactions",
        "status",
        existing_type=postgresql.ENUM(
            "PENDING",
            "COMPLETED",
            "FAILED",
            name="fiattransactionstatus",
        ),
        type_=sa.String(length=20),
        postgresql_using="status::text",
    )

    postgresql.ENUM(name="fiattransactiontype").drop(
        op.get_bind(), checkfirst=True
    )

    postgresql.ENUM(name="fiattransactionstatus").drop(
        op.get_bind(), checkfirst=True
    )