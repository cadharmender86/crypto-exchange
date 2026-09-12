"""add contract address to assets

Revision ID: 81fc702e5872
Revises: 3a5e867e6142
Create Date: 2026-09-12 17:46:26.739979

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81fc702e5872'
down_revision: Union[str, Sequence[str], None] = '3a5e867e6142'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assets",
        sa.Column(
            "contract_address",
            sa.String(length=255),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("assets", "contract_address")