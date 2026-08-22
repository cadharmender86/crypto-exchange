from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as sqlEnum

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

from app.models.fiat_account import FiatAccount
from app.models.user import User


class FiatTransactionType(str, Enum):
    INR_DEPOSIT = "INR_DEPOSIT"
    INR_WITHDRAWAL = "INR_WITHDRAWAL"

    TRADE_BUY = "TRADE_BUY"
    TRADE_SELL = "TRADE_SELL"

    WITHDRAWAL_LOCK = "WITHDRAWAL_LOCK"
    WITHDRAWAL_UNLOCK = "WITHDRAWAL_UNLOCK"

    REFUND = "REFUND"
    FEE = "FEE"


class FiatTransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class FiatTransaction(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "fiat_transactions"

    fiat_account_id: Mapped[UUID] = mapped_column(
        ForeignKey("fiat_accounts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    transaction_type: Mapped[FiatTransactionType] = mapped_column(
        sqlEnum(FiatTransactionType),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(38, 18),
        nullable=False,
    )

    balance_after: Mapped[Decimal] = mapped_column(
        Numeric(38, 18),
        nullable=False,
    )

    reference_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    reference_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    idempotency_key: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )

    status: Mapped[FiatTransactionStatus] = mapped_column(
        sqlEnum(FiatTransactionStatus),
        nullable=False,
        default=FiatTransactionStatus.COMPLETED,
        
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    fiat_account: Mapped["FiatAccount"] = relationship(
        back_populates="transactions"
    )

    user: Mapped["User"] = relationship(
        back_populates="fiat_transactions"
    )