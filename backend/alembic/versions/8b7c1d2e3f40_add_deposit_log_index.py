"""add deposit log index

Revision ID: 8b7c1d2e3f40
Revises: 7a1c2d9e4f10, f1a2b3c4d5e6
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect
from alembic import op


revision: str = "8b7c1d2e3f40"
down_revision: str | Sequence[str] | None = ("7a1c2d9e4f10", "f1a2b3c4d5e6")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # Existing columns
    columns = {col["name"] for col in inspector.get_columns("deposits")}

    if "blockchain_log_index" not in columns:
        op.add_column(
            "deposits",
            sa.Column("blockchain_log_index", sa.Integer(), nullable=True),
        )

    # Existing indexes
    indexes = {idx["name"] for idx in inspector.get_indexes("deposits")}

    if "ix_deposits_blockchain_log_index" not in indexes:
        op.create_index(
            "ix_deposits_blockchain_log_index",
            "deposits",
            ["blockchain_log_index"],
            unique=False,
        )


def downgrade() -> None:
    op.drop_constraint(
        "uq_deposit_network_tx_log",
        "deposits",
        type_="unique",
    )
    op.drop_column("deposits", "blockchain_log_index")
    op.create_unique_constraint(
        "uq_deposit_network_tx_hash",
        "deposits",
        ["network", "blockchain_tx_hash"],
    )
