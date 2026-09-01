"""merge fiat account and deposit branches

Revision ID: 973f8252daf4
Revises: 11519e64b885, 93c703e8b6f2
Create Date: 2026-08-24 17:26:25.153368

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '973f8252daf4'
down_revision: Union[str, Sequence[str], None] = ('11519e64b885', '93c703e8b6f2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    pass


def downgrade() -> None:
    """Downgrade database schema."""
    pass