from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import Boolean, Enum as SqlEnum
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class BankAccountStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    DISABLED = "DISABLED"


class BankAccountType(str, Enum):
    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"


class BankAccount(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "bank_accounts"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "account_number",
            "ifsc_code",
            name="uq_user_bank_account",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    account_holder_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    bank_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    account_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    ifsc_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    account_type: Mapped[BankAccountType] = mapped_column(
        SqlEnum(BankAccountType),
        default=BankAccountType.SAVINGS,
        nullable=False,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    status: Mapped[BankAccountStatus] = mapped_column(
        SqlEnum(BankAccountStatus),
        default=BankAccountStatus.PENDING,
        nullable=False,
    )

    verification_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="bank_accounts",
    )