"""add rejection reason to kyc documents

Revision ID: fcc7d7901fff
Revises: 3ddc4ce18c1c
Create Date: 2026-09-08 07:50:04.803824

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcc7d7901fff'
down_revision: Union[str, Sequence[str], None] = '3ddc4ce18c1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "kyc_documents",
        sa.Column(
            "rejection_reason",
            sa.Text(),
            nullable=True,
        ),
    )

def downgrade():
    op.drop_column("kyc_documents", "rejection_reason")