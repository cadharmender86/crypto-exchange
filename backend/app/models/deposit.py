from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Deposit(Base):
    __tablename__ = "deposits"

    __table_args__ = (
        UniqueConstraint(
            "network",
            "blockchain_tx_hash",
            "blockchain_log_index",
            name="uq_deposit_network_tx_log",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    wallet_address_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("wallet_addresses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    asset_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    network: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    blockchain_tx_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    blockchain_log_index: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(38, 18),
        nullable=False,
    )

    confirmations: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
        index=True,
    )

    ledger_transaction_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("ledger_transactions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    # -----------------------------
    # Relationships
    # -----------------------------

    user = relationship(
        "User",
        back_populates="deposits",
    )

    wallet_address = relationship(
        "WalletAddress",
        back_populates="deposits",
    )

    asset = relationship(
        "Asset",
        back_populates="deposits",
    )

    ledger_transaction = relationship(
        "LedgerTransaction",
        back_populates="deposits",
    )