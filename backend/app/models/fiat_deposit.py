from decimal import Decimal
from enum import Enum
from uuid import UUID
from datetime import datetime

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FiatDepositStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class FiatDeposit(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "fiat_deposits"

    # User making deposit
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Bank account used for deposit
    bank_account_id: Mapped[UUID] = mapped_column(
        ForeignKey("bank_accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Ledger transaction created after approval
    ledger_transaction_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ledger_transactions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(38, 18),
        nullable=False,
    )

    utr_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    status: Mapped[FiatDepositStatus] = mapped_column(
        SqlEnum(FiatDepositStatus),
        default=FiatDepositStatus.PENDING,
        nullable=False,
        index=True,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    rejection_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    approved_by_admin_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("admin_users.id"),
        nullable=True,
        index=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Bank webhook/manual metadata
    provider_metadata: Mapped[dict | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )

    # Relationships

    user: Mapped["User"] = relationship(
        "User",
        back_populates="fiat_deposits",
        lazy="selectin",
    )

    bank_account: Mapped["BankAccount"] = relationship(
        "BankAccount",
        back_populates="fiat_deposits",
        lazy="selectin",
    )

    ledger_transaction: Mapped["LedgerTransaction | None"] = relationship(
        "LedgerTransaction",
        back_populates="fiat_deposits",
        lazy="selectin",
    )