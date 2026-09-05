"""phase_8_1_unified_ledger

Revision ID: 15e7e0afdf92
Revises: e35245529860
Create Date: 2026-09-05 12:22:39.521349

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '15e7e0afdf92'
down_revision: Union[str, Sequence[str], None] = 'e35245529860'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =====================================================
    # Phase 8.1 - Unified Ledger Schema
    # =====================================================

    # ---------- Create PostgreSQL ENUMs ----------
    ledger_transaction_type_enum = postgresql.ENUM(
        "INR_DEPOSIT",
        "INR_WITHDRAWAL",
        "CRYPTO_DEPOSIT",
        "CRYPTO_WITHDRAWAL",
        "TRADE_BUY",
        "TRADE_SELL",
        "INTERNAL_TRANSFER",
        "FEE",
        "REFUND",
        name="ledger_transaction_type_enum",
    )
    ledger_transaction_type_enum.create(op.get_bind(), checkfirst=True)

    ledger_transaction_status_enum = postgresql.ENUM(
        "PENDING",
        "POSTED",
        "FAILED",
        "CANCELLED",
        name="ledger_transaction_status_enum",
    )
    ledger_transaction_status_enum.create(op.get_bind(), checkfirst=True)

    ledger_entry_type_enum = postgresql.ENUM(
        "DEBIT",
        "CREDIT",
        name="ledger_entry_type_enum",
    )
    ledger_entry_type_enum.create(op.get_bind(), checkfirst=True)

    # ---------- ledger_transactions ----------
    op.add_column(
        "ledger_transactions",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,  # Existing rows have no user yet.
        ),
    )

    op.create_index(
        "ix_ledger_transactions_user_id",
        "ledger_transactions",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_ledger_transactions_status",
        "ledger_transactions",
        ["status"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_ledger_transactions_user",
        "ledger_transactions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.alter_column(
        "ledger_transactions",
        "transaction_type",
        existing_type=sa.String(length=30),
        type_=ledger_transaction_type_enum,
        postgresql_using="transaction_type::ledger_transaction_type_enum",
    )

    op.alter_column(
        "ledger_transactions",
        "status",
        existing_type=sa.String(length=20),
        type_=ledger_transaction_status_enum,
        postgresql_using="status::ledger_transaction_status_enum",
    )

    # ---------- ledger_entries ----------
    op.alter_column(
        "ledger_entries",
        "entry_type",
        existing_type=sa.String(length=10),
        type_=ledger_entry_type_enum,
        postgresql_using="entry_type::ledger_entry_type_enum",
    )


def downgrade():
    op.alter_column(
        "ledger_entries",
        "entry_type",
        type_=sa.String(length=10),
        postgresql_using="entry_type::text",
    )

    op.alter_column(
        "ledger_transactions",
        "status",
        type_=sa.String(length=20),
        postgresql_using="status::text",
    )

    op.alter_column(
        "ledger_transactions",
        "transaction_type",
        type_=sa.String(length=30),
        postgresql_using="transaction_type::text",
    )

    op.drop_constraint(
        "fk_ledger_transactions_user",
        "ledger_transactions",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_ledger_transactions_user_id",
        table_name="ledger_transactions",
    )

    op.drop_index(
        "ix_ledger_transactions_status",
        table_name="ledger_transactions",
    )

    op.drop_column("ledger_transactions", "user_id")

    postgresql.ENUM(name="ledger_entry_type_enum").drop(
        op.get_bind(),
        checkfirst=True,
    )

    postgresql.ENUM(name="ledger_transaction_status_enum").drop(
        op.get_bind(),
        checkfirst=True,
    )

    postgresql.ENUM(name="ledger_transaction_type_enum").drop(
        op.get_bind(),
        checkfirst=True,
    )