"""add withdrawal rejection audit fields

Revision ID: af8b9ed23404
Revises: ca729d3d207b
Create Date: 2026-09-12 18:30:37.035968

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = 'af8b9ed23404'
down_revision: Union[str, Sequence[str], None] = 'ca729d3d207b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "withdrawals",
        sa.Column("rejected_by", UUID(as_uuid=True), nullable=True),
    )

    op.add_column(
        "withdrawals",
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_foreign_key(
        "fk_withdrawals_rejected_by_admin",
        "withdrawals",
        "admin_users",
        ["rejected_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint(
        "fk_withdrawals_rejected_by_admin",
        "withdrawals",
        type_="foreignkey",
    )

    op.drop_column("withdrawals", "rejected_at")
    op.drop_column("withdrawals", "rejected_by")