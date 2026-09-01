"""add withdrawal finance approval fields

Revision ID: a2eb46ca5394
Revises: 973f8252daf4
Create Date: 2026-08-24
"""

from typing import Sequence, Union

from sqlalchemy import inspect
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision: str = "a2eb46ca5394"
down_revision: Union[str, Sequence[str], None] = "973f8252daf4"
branch_labels = None
depends_on = None

def add_column_if_missing(table_name, column):
    bind = op.get_bind()
    inspector = inspect(bind)

    existing = {c["name"] for c in inspector.get_columns(table_name)}

    if column.name not in existing:
        op.add_column(table_name, column)


def upgrade():
    add_column_if_missing(
        "withdrawals",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    add_column_if_missing(
        "withdrawals",
        sa.Column("bank_account_id", sa.UUID(), nullable=True),
    )

    add_column_if_missing(
        "withdrawals",
        sa.Column("approved_by_admin_id", sa.UUID(), nullable=True),
    )

    add_column_if_missing(
        "withdrawals",
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
    )

    add_column_if_missing(
        "withdrawals",
        sa.Column("utr_number", sa.String(length=100), nullable=True),
    )

    add_column_if_missing(
        "withdrawals",
        sa.Column("provider", sa.String(length=50), nullable=True),
    )

    add_column_if_missing(
        "withdrawals",
        sa.Column("provider_reference", sa.String(length=100), nullable=True),
    )

    add_column_if_missing(
        "withdrawals",
        sa.Column("rejection_reason", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_withdrawals_admin_user",
        "withdrawals",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_withdrawals_bank_account",
        "withdrawals",
        type_="foreignkey",
    )

    op.drop_index("ix_withdrawals_utr_number", table_name="withdrawals")
    op.drop_index("ix_withdrawals_approved_by_admin_id", table_name="withdrawals")
    op.drop_index("ix_withdrawals_bank_account_id", table_name="withdrawals")

    op.drop_column("withdrawals", "rejection_reason")
    op.drop_column("withdrawals", "provider_reference")
    op.drop_column("withdrawals", "provider")
    op.drop_column("withdrawals", "utr_number")
    op.drop_column("withdrawals", "completed_at")
    op.drop_column("withdrawals", "approved_at")
    op.drop_column("withdrawals", "approved_by_admin_id")
    op.drop_column("withdrawals", "bank_account_id")