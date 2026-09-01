from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

from enum import Enum


class WithdrawalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    BROADCASTING = "BROADCASTING"
    BROADCASTED = "BROADCASTED"
    # PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    # CANCELLED = "CANCELLED"

class Withdrawal(Base):
    __tablename__ = "withdrawals"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "idempotency_key",
            name="uq_withdrawal_user_idempotency_key",
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

    account_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="RESTRICT"),
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

    destination_address: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(38, 18),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=WithdrawalStatus.PENDING.value,
        index=True,
    )

    blockchain_tx_hash: Mapped[str | None] = mapped_column(
        String(66),
        nullable=True,
        unique=True,
        index=True,
    )

    confirmations: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )
    
    failure_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    ledger_transaction_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("ledger_transactions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    broadcasted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
        back_populates="withdrawals",
    )

    asset = relationship(
        "Asset",
        back_populates="withdrawals",
    )

    ledger_transaction = relationship(
        "LedgerTransaction",
        back_populates="withdrawals",
    )


    # ------------------------------------------------------------------
    # Finance approval workflow
    # ------------------------------------------------------------------

    bank_account_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("bank_accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    approved_by_admin_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("admin_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    utr_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
    )

    provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    provider_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    rejection_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    bank_account: Mapped["BankAccount"] = relationship(
        "BankAccount",
        back_populates="withdrawals",
    )

    ledger_transaction: Mapped["LedgerTransaction | None"] = relationship(
        "LedgerTransaction",
        back_populates="withdrawals",
    )

    approved_by_admin: Mapped["AdminUser | None"] = relationship(
        "AdminUser",
        foreign_keys=[approved_by_admin_id],
    )