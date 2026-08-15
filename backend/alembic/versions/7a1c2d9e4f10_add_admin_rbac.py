"""add admin RBAC schema and seed permissions

Revision ID: 7a1c2d9e4f10
Revises: 4564185a6bfd
Create Date: 2026-08-15

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7a1c2d9e4f10"
down_revision: Union[str, Sequence[str], None] = "4564185a6bfd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PERMISSIONS = [
    ("USER_READ", "View customer accounts"),
    ("USER_SUSPEND", "Suspend customer accounts"),
    ("USER_ACTIVATE", "Activate customer accounts"),
    ("KYC_READ", "View KYC records"),
    ("KYC_APPROVE", "Approve KYC"),
    ("KYC_REJECT", "Reject KYC"),
    ("DEPOSIT_READ", "View deposits"),
    ("WITHDRAWAL_READ", "View withdrawals"),
    ("WITHDRAWAL_APPROVE", "Approve withdrawals"),
    ("WITHDRAWAL_REJECT", "Reject withdrawals"),
    ("LEDGER_READ", "View ledger entries"),
    ("RECONCILIATION_READ", "View reconciliation data"),
    ("ORDER_READ", "View orders"),
    ("TRADE_READ", "View trades"),
    ("AUDIT_READ", "View audit logs"),
    ("ADMIN_MANAGE", "Manage administrator accounts and RBAC"),
]

ROLES = [
    ("SUPER_ADMIN", "Full administrative access"),
    ("OPERATIONS_ADMIN", "Customer and operational access"),
    ("KYC_ADMIN", "KYC operations"),
    ("FINANCE_ADMIN", "Deposits, withdrawals and ledger operations"),
    ("TRADING_ADMIN", "Trading operations"),
    ("SUPPORT_ADMIN", "Customer support operations"),
    ("AUDITOR", "Read-only audit access"),
]

ROLE_PERMISSIONS = {
    "OPERATIONS_ADMIN": ["USER_READ", "USER_SUSPEND", "USER_ACTIVATE", "DEPOSIT_READ", "WITHDRAWAL_READ"],
    "KYC_ADMIN": ["USER_READ", "KYC_READ", "KYC_APPROVE", "KYC_REJECT"],
    "FINANCE_ADMIN": ["DEPOSIT_READ", "WITHDRAWAL_READ", "WITHDRAWAL_APPROVE", "WITHDRAWAL_REJECT", "LEDGER_READ", "RECONCILIATION_READ"],
    "TRADING_ADMIN": ["ORDER_READ", "TRADE_READ"],
    "SUPPORT_ADMIN": ["USER_READ", "USER_SUSPEND", "USER_ACTIVATE", "KYC_READ", "DEPOSIT_READ", "WITHDRAWAL_READ"],
    "AUDITOR": ["USER_READ", "KYC_READ", "DEPOSIT_READ", "WITHDRAWAL_READ", "LEDGER_READ", "RECONCILIATION_READ", "ORDER_READ", "TRADE_READ", "AUDIT_READ"],
}


def upgrade() -> None:
    op.create_table(
        "admin_users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("is_locked", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("failed_login_attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_admin_users_email", "admin_users", ["email"], unique=False)

    op.create_table(
        "admin_roles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_admin_roles_name", "admin_roles", ["name"], unique=False)

    op.create_table(
        "admin_permissions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_admin_permissions_name", "admin_permissions", ["name"], unique=False)

    op.create_table(
        "admin_user_roles",
        sa.Column("admin_user_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["admin_user_id"], ["admin_users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["admin_roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("admin_user_id", "role_id"),
    )

    op.create_table(
        "admin_role_permissions",
        sa.Column("role_id", sa.UUID(), nullable=False),
        sa.Column("permission_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["admin_roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["permission_id"], ["admin_permissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("admin_user_id", sa.UUID(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=255), nullable=True),
        sa.Column("old_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=1000), nullable=True),
        sa.Column("result", sa.String(length=30), nullable=False),
        sa.Column("reason", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["admin_user_id"], ["admin_users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_admin_user_id", "audit_logs", ["admin_user_id"], unique=False)
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)
    op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"], unique=False)
    op.create_index("ix_audit_logs_resource_id", "audit_logs", ["resource_id"], unique=False)

    for name, description in PERMISSIONS:
        op.execute(
            sa.text(
                "INSERT INTO admin_permissions (id, name, description) "
                "VALUES (gen_random_uuid(), :name, :description)"
            ).bindparams(name=name, description=description)
        )

    for name, description in ROLES:
        op.execute(
            sa.text(
                "INSERT INTO admin_roles (id, name, description) "
                "VALUES (gen_random_uuid(), :name, :description)"
            ).bindparams(name=name, description=description)
        )

    # SUPER_ADMIN intentionally receives all permissions.
    op.execute(
        sa.text(
            "INSERT INTO admin_role_permissions (role_id, permission_id) "
            "SELECT r.id, p.id FROM admin_roles r CROSS JOIN admin_permissions p "
            "WHERE r.name = 'SUPER_ADMIN'"
        )
    )

    for role_name, permission_names in ROLE_PERMISSIONS.items():
        for permission_name in permission_names:
            op.execute(
                sa.text(
                    "INSERT INTO admin_role_permissions (role_id, permission_id) "
                    "SELECT r.id, p.id FROM admin_roles r, admin_permissions p "
                    "WHERE r.name = :role_name AND p.name = :permission_name"
                ).bindparams(role_name=role_name, permission_name=permission_name)
            )


def downgrade() -> None:
    op.drop_index("ix_audit_logs_resource_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_resource_type", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_admin_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_table("admin_role_permissions")
    op.drop_table("admin_user_roles")
    op.drop_index("ix_admin_permissions_name", table_name="admin_permissions")
    op.drop_table("admin_permissions")
    op.drop_index("ix_admin_roles_name", table_name="admin_roles")
    op.drop_table("admin_roles")
    op.drop_index("ix_admin_users_email", table_name="admin_users")
    op.drop_table("admin_users")
