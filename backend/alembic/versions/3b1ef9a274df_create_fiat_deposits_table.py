"""create fiat deposits table

Revision ID: 3b1ef9a274df
Revises: 271bad75ad5f
Create Date: 2026-08-23 19:01:15.898822

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b1ef9a274df'
down_revision: Union[str, Sequence[str], None] = '271bad75ad5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fiat_deposits",

        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("bank_account_id", sa.UUID(), nullable=False),
        sa.Column("ledger_transaction_id", sa.UUID(), nullable=True),

        sa.Column(
            "currency",
            sa.String(length=10),
            nullable=False,
            server_default="INR",
        ),

        sa.Column(
            "amount",
            sa.Numeric(precision=38, scale=18),
            nullable=False,
        ),

        sa.Column("utr_number", sa.String(length=50), nullable=False),

        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "APPROVED",
                "REJECTED",
                "EXPIRED",
                name="fiatdepositstatus",
            ),
            nullable=False,
        ),

        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),

        sa.Column("approved_by_admin_id", sa.UUID(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),

        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),

        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["bank_account_id"],
            ["bank_accounts.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["ledger_transaction_id"],
            ["ledger_transactions.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["approved_by_admin_id"],
            ["admin_users.id"],
            ondelete="SET NULL",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_fiat_deposits_approved_by_admin_id"),
        "fiat_deposits",
        ["approved_by_admin_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_fiat_deposits_bank_account_id"),
        "fiat_deposits",
        ["bank_account_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_fiat_deposits_ledger_transaction_id"),
        "fiat_deposits",
        ["ledger_transaction_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_fiat_deposits_status"),
        "fiat_deposits",
        ["status"],
        unique=False,
    )

    op.create_index(
        op.f("ix_fiat_deposits_user_id"),
        "fiat_deposits",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_fiat_deposits_utr_number"),
        "fiat_deposits",
        ["utr_number"],
        unique=True,
    )

    op.create_index(
        "ix_fiat_deposits_user_status",
        "fiat_deposits",
        ["user_id", "status"],
        unique=False,
    )

    op.create_index(
        "ix_fiat_deposits_created_at",
        "fiat_deposits",
        ["created_at"],
        unique=False,
    )
    

def downgrade():
    op.drop_index("ix_fiat_deposits_created_at", table_name="fiat_deposits")
    op.drop_index("ix_fiat_deposits_user_status", table_name="fiat_deposits")
    op.drop_index(op.f("ix_fiat_deposits_utr_number"), table_name="fiat_deposits")
    op.drop_index(op.f("ix_fiat_deposits_user_id"), table_name="fiat_deposits")
    op.drop_index(op.f("ix_fiat_deposits_status"), table_name="fiat_deposits")
    op.drop_index(op.f("ix_fiat_deposits_bank_account_id"), table_name="fiat_deposits")
    op.drop_index(op.f("ix_fiat_deposits_ledger_transaction_id"), table_name="fiat_deposits")
    op.drop_index(op.f("ix_fiat_deposits_approved_by_admin_id"), table_name="fiat_deposits")

    op.drop_table("fiat_deposits")