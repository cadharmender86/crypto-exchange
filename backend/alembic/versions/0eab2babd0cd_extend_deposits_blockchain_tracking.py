"""extend deposits blockchain tracking

Revision ID: 0eab2babd0cd
Revises: 81fc702e5872
Create Date: 2026-09-12 18:23:57.877604

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0eab2babd0cd'
down_revision: Union[str, Sequence[str], None] = '81fc702e5872'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "deposits",
        sa.Column("block_number", sa.BigInteger(), nullable=True),
    )

    op.add_column(
        "deposits",
        sa.Column("failure_reason", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "deposits",
        sa.Column("broadcasted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.add_column(
        "deposits",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

def downgrade():
    op.drop_column("deposits", "completed_at")
    op.drop_column("deposits", "broadcasted_at")
    op.drop_column("deposits", "failure_reason")
    op.drop_column("deposits", "block_number")