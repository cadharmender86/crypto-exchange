"""add blockchain cursor table

Revision ID: 6a209c39f2a3
Revises: 15e7e0afdf92
Create Date: 2026-09-06 15:19:03.833974
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision: str = "6a209c39f2a3"
down_revision: Union[str, Sequence[str], None] = "15e7e0afdf92"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "blockchain_cursors",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "network",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "last_processed_block",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_blockchain_cursors_network",
        "blockchain_cursors",
        ["network"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_blockchain_cursors_network",
        table_name="blockchain_cursors",
    )

    op.drop_table("blockchain_cursors")