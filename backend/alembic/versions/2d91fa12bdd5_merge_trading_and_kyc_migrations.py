"""merge trading and kyc migrations

Revision ID: 2d91fa12bdd5
Revises: 9c3e5f7a2b41, c9d2e3f40512
Create Date: 2026-08-17 16:14:45.455267

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d91fa12bdd5'
down_revision: Union[str, Sequence[str], None] = ('9c3e5f7a2b41', 'c9d2e3f40512')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    pass


def downgrade() -> None:
    """Downgrade database schema."""
    pass