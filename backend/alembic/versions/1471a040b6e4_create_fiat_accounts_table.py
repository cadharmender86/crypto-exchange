"""create fiat_accounts table

Revision ID: 1471a040b6e4
Revises: 8b7c1d2e3f40
Create Date: 2026-08-22 20:06:25.433407

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1471a040b6e4'
down_revision: Union[str, Sequence[str], None] = '8b7c1d2e3f40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fiat_accounts",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("available_balance", sa.Numeric(38, 18), nullable=False),
        sa.Column("locked_balance", sa.Numeric(38, 18), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),

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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "currency",
            name="uq_fiat_account_user_currency",
        ),
    )

    op.create_index(
        "ix_fiat_accounts_user_id",
        "fiat_accounts",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_fiat_accounts_user_id",
        table_name="fiat_accounts",
    )

    op.drop_table("fiat_accounts")