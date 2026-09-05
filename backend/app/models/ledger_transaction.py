from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from app.models.user import User
from sqlalchemy import Enum as SqlEnum, ForeignKey, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class LedgerTransactionType(str, Enum):
    INR_DEPOSIT = "INR_DEPOSIT"
    INR_WITHDRAWAL = "INR_WITHDRAWAL"

    CRYPTO_DEPOSIT = "CRYPTO_DEPOSIT"
    CRYPTO_WITHDRAWAL = "CRYPTO_WITHDRAWAL"

    TRADE_BUY = "TRADE_BUY"
    TRADE_SELL = "TRADE_SELL"

    INTERNAL_TRANSFER = "INTERNAL_TRANSFER"

    FEE = "FEE"
    REFUND = "REFUND"


class LedgerTransactionStatus(str, Enum):
    PENDING = "PENDING"
    POSTED = "POSTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class LedgerTransaction(Base):
    __tablename__ = "ledger_transactions"

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

    reference: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    transaction_type: Mapped[LedgerTransactionType] = mapped_column(
        SqlEnum(LedgerTransactionType, name="ledger_transaction_type_enum"),
        nullable=False,
        index=True,
    )

    status: Mapped[LedgerTransactionStatus] = mapped_column(
        SqlEnum(LedgerTransactionStatus, name="ledger_transaction_status_enum"),
        nullable=False,
        default=LedgerTransactionStatus.POSTED,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    deposits: Mapped[list["Deposit"]] = relationship(
        "Deposit",
        back_populates="ledger_transaction",
        lazy="selectin",
        order_by="Deposit.created_at.desc()",
    )

    withdrawals: Mapped[list["Withdrawal"]] = relationship(
        "Withdrawal",
        back_populates="ledger_transaction",
        lazy="selectin",
        order_by="Withdrawal.created_at.desc()",
    )

    ledger_entries: Mapped[list["LedgerEntry"]] = relationship(
        "LedgerEntry",
        back_populates="ledger_transaction",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    fiat_deposits: Mapped[list["FiatDeposit"]] = relationship(
        "FiatDeposit",
        back_populates="ledger_transaction",
        lazy="selectin",
        order_by="FiatDeposit.created_at.desc()",
    )

    user: Mapped["User"] = relationship(
    "User",
    back_populates="ledger_transactions",
)