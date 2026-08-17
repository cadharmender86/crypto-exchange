"""add KYC review permission

Revision ID: 9c3e5f7a2b41
Revises: 8b2f4c6d1e30
Create Date: 2026-08-15

"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision: str = "9c3e5f7a2b41"
down_revision: Union[str, Sequence[str], None] = "8b2f4c6d1e30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    permission_id = uuid4()
    op.execute(
        sa.text(
            "INSERT INTO admin_permissions (id, name, description) VALUES (:id, :name, :description)"
        ).bindparams(
            id=permission_id,
            name="KYC_REVIEW",
            description="Move KYC records into review state",
        )
    )

    op.execute(
        sa.text(
            "INSERT INTO admin_role_permissions (role_id, permission_id) "
            "SELECT id, :permission_id FROM admin_roles WHERE name = 'KYC_ADMIN'"
        ).bindparams(permission_id=permission_id)
    )
    op.execute(
        sa.text(
            "INSERT INTO admin_role_permissions (role_id, permission_id) "
            "SELECT id, :permission_id FROM admin_roles WHERE name = 'SUPER_ADMIN'"
        ).bindparams(permission_id=permission_id)
    )


def downgrade() -> None:
    permission = op.get_bind().execute(
        sa.text("SELECT id FROM admin_permissions WHERE name = 'KYC_REVIEW'")
    ).scalar_one_or_none()
    if permission is not None:
        op.execute(
            sa.text("DELETE FROM admin_role_permissions WHERE permission_id = :permission_id")
            .bindparams(permission_id=permission)
        )
        op.execute(
            sa.text("DELETE FROM admin_permissions WHERE id = :permission_id")
            .bindparams(permission_id=permission)
        )
