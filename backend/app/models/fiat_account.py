from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class FiatAccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class FiatAccount(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "fiat_accounts"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "currency",
            name="uq_fiat_account_user_currency",
        ),
    )

    # User owning this INR wallet
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # INR only for BitNova v1
    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False,
    )

    # Spendable INR balance
    available_balance: Mapped[Decimal] = mapped_column(
        Numeric(38, 18),
        default=Decimal("0"),
        nullable=False,
    )

    # Locked INR (withdrawals, open buy orders)
    locked_balance: Mapped[Decimal] = mapped_column(
        Numeric(38, 18),
        default=Decimal("0"),
        nullable=False,
    )

    status: Mapped[FiatAccountStatus] = mapped_column(
        SqlEnum(FiatAccountStatus),
        default=FiatAccountStatus.ACTIVE,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="fiat_accounts",
    )

    transactions: Mapped[list["FiatTransaction"]] = relationship(
        "FiatTransaction",
        back_populates="fiat_account",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="FiatTransaction.created_at.desc()",
    )