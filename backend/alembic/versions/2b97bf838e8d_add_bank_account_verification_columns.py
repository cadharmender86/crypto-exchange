"""add bank account verification columns"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2b97bf838e8d"   # keep generated revision
down_revision: Union[str, Sequence[str], None] = "4f5651ffe6aa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "bank_accounts",
        sa.Column("account_type", sa.String(length=30), nullable=True),
    )

    op.add_column(
        "bank_accounts",
        sa.Column("verification_reference", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "bank_accounts",
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("bank_accounts", "verified_at")
    op.drop_column("bank_accounts", "verification_reference")
    op.drop_column("bank_accounts", "account_type")