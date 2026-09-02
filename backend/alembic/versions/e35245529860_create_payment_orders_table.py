"""create_payment_orders_table

Revision ID: e35245529860
Revises: a2eb46ca5394
Create Date: 2026-09-01 23:19:51.502144

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e35245529860'
down_revision: Union[str, Sequence[str], None] = 'a2eb46ca5394'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


payment_gateway_enum = postgresql.ENUM(
    "CASHFREE",
    name="payment_gateway_enum",
    create_type=False,
)

payment_order_status_enum = postgresql.ENUM(
    "CREATED",
    "PENDING",
    "SUCCESS",
    "FAILED",
    "EXPIRED",
    "CANCELLED",
    name="payment_order_status_enum",
    create_type=False,
)


def upgrade():
    payment_gateway_enum.create(op.get_bind(), checkfirst=True)
    payment_order_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "payment_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("gateway", payment_gateway_enum, nullable=False),
        sa.Column("gateway_order_id", sa.String(length=100), nullable=False),
        sa.Column("payment_session_id", sa.String(length=255)),
        sa.Column("amount", sa.Numeric(18, 8), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("payment_method", sa.String(length=30)),
        sa.Column("status", payment_order_status_enum, nullable=False),
        sa.Column("gateway_payment_id", sa.String(length=150)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("failure_reason", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_payment_orders_user_id",
        "payment_orders",
        ["user_id"],
    )
    op.create_index(
        "ix_payment_orders_gateway_order_id",
        "payment_orders",
        ["gateway_order_id"],
        unique=True,
    )
    op.create_index(
        "ix_payment_orders_gateway_payment_id",
        "payment_orders",
        ["gateway_payment_id"],
    )
    op.create_index(
        "ix_payment_orders_status",
        "payment_orders",
        ["status"],
    )


def downgrade():
    op.drop_index("ix_payment_orders_status", table_name="payment_orders")
    op.drop_index("ix_payment_orders_gateway_payment_id", table_name="payment_orders")
    op.drop_index("ix_payment_orders_gateway_order_id", table_name="payment_orders")
    op.drop_index("ix_payment_orders_user_id", table_name="payment_orders")

    op.drop_table("payment_orders")

    payment_order_status_enum.drop(op.get_bind(), checkfirst=True)
    payment_gateway_enum.drop(op.get_bind(), checkfirst=True)