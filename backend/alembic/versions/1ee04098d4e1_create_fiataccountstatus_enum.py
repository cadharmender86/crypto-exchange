"""create fiataccountstatus enum"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "1ee04098d4e1"
down_revision: Union[str, Sequence[str], None] = "8fca1e304c44"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create PostgreSQL enum type
    fiat_status = postgresql.ENUM(
        "ACTIVE",
        "FROZEN",
        "CLOSED",
        name="fiataccountstatus",
    )

    fiat_status.create(op.get_bind(), checkfirst=True)

    # Convert existing VARCHAR column to ENUM
    op.alter_column(
        "fiat_accounts",
        "status",
        existing_type=sa.String(length=20),
        type_=fiat_status,
        postgresql_using="status::fiataccountstatus",
    )


def downgrade() -> None:
    # Convert ENUM back to VARCHAR
    op.alter_column(
        "fiat_accounts",
        "status",
        existing_type=postgresql.ENUM(
            "ACTIVE",
            "FROZEN",
            "CLOSED",
            name="fiataccountstatus",
        ),
        type_=sa.String(length=20),
        postgresql_using="status::text",
    )

    fiat_status = postgresql.ENUM(
        "ACTIVE",
        "FROZEN",
        "CLOSED",
        name="fiataccountstatus",
    )

    fiat_status.drop(op.get_bind(), checkfirst=True)