"""create bank_accounts table

Revision ID: 11519e64b885
Revises: 1471a040b6e4
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "11519e64b885"
down_revision: Union[str, Sequence[str], None] = "1471a040b6e4"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # -----------------------------
    # Bank Accounts
    # -----------------------------
    op.create_table(
        "bank_accounts",

        sa.Column("user_id", sa.UUID(), nullable=False),

        sa.Column("account_holder_name", sa.String(150), nullable=False),
        sa.Column("bank_name", sa.String(150), nullable=False),
        sa.Column("account_number", sa.String(50), nullable=False),
        sa.Column("ifsc_code", sa.String(20), nullable=False),

        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.String(20), nullable=False),

        sa.Column("id", sa.UUID(), nullable=False),
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

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_bank_accounts_user_id",
        "bank_accounts",
        ["user_id"],
    )

    op.create_index(
        "ix_bank_accounts_ifsc_code",
        "bank_accounts",
        ["ifsc_code"],
    )

    # -----------------------------
    # Fiat Transactions
    # -----------------------------
    op.create_table(
        "fiat_transactions",

        sa.Column("fiat_account_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),

        sa.Column("transaction_type", sa.String(50), nullable=False),

        sa.Column("amount", sa.Numeric(38, 18), nullable=False),
        sa.Column("balance_after", sa.Numeric(38, 18), nullable=False),

        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("reference_id", sa.String(255), nullable=True),

        sa.Column("status", sa.String(20), nullable=False),

        sa.Column("description", sa.String(500), nullable=True),

        sa.Column("idempotency_key", sa.String(255), nullable=True),

        sa.Column("id", sa.UUID(), nullable=False),
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

        sa.ForeignKeyConstraint(
            ["fiat_account_id"],
            ["fiat_accounts.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_fiat_transactions_fiat_account_id",
        "fiat_transactions",
        ["fiat_account_id"],
    )

    op.create_index(
        "ix_fiat_transactions_user_id",
        "fiat_transactions",
        ["user_id"],
    )

    op.create_index(
        "ix_fiat_transactions_transaction_type",
        "fiat_transactions",
        ["transaction_type"],
    )

    op.create_index(
        "ix_fiat_transactions_reference_id",
        "fiat_transactions",
        ["reference_id"],
    )

    op.create_index(
        "ix_fiat_transactions_idempotency_key",
        "fiat_transactions",
        ["idempotency_key"],
        unique=True,
    )


def downgrade() -> None:

    op.drop_index("ix_fiat_transactions_idempotency_key", table_name="fiat_transactions")
    op.drop_index("ix_fiat_transactions_reference_id", table_name="fiat_transactions")
    op.drop_index("ix_fiat_transactions_transaction_type", table_name="fiat_transactions")
    op.drop_index("ix_fiat_transactions_user_id", table_name="fiat_transactions")
    op.drop_index("ix_fiat_transactions_fiat_account_id", table_name="fiat_transactions")
    op.drop_table("fiat_transactions")

    op.drop_index("ix_bank_accounts_ifsc_code", table_name="bank_accounts")
    op.drop_index("ix_bank_accounts_user_id", table_name="bank_accounts")
    op.drop_table("bank_accounts")