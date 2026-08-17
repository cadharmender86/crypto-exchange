"""add contract address to assets

Revision ID: a5f42626c932
Revises: 165c11a9bf7d
Create Date: 2026-08-18 04:28:25.366140

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5f42626c932'
down_revision: Union[str, Sequence[str], None] = '165c11a9bf7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    op.add_column(
        "assets",
        sa.Column(
            "contract_address",
            sa.String(length=255),
            nullable=True,
        ),
    )



def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_column("assets", "contract_address")
