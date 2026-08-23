from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class User(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    two_factor_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # -----------------------------
    # Wallet Relationships
    # -----------------------------

    accounts: Mapped[list["Account"]] = relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    fiat_accounts: Mapped[list["FiatAccount"]] = relationship(
        "FiatAccount",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    fiat_transactions: Mapped[list["FiatTransaction"]] = relationship(
        "FiatTransaction",
        back_populates="user",
        lazy="selectin",
        order_by="FiatTransaction.created_at.desc()",
    )

    wallet_addresses: Mapped[list["WalletAddress"]] = relationship(
        "WalletAddress",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    deposits: Mapped[list["Deposit"]] = relationship(
        "Deposit",
        back_populates="user",
        lazy="selectin",
        order_by="Deposit.created_at.desc()",
    )

    withdrawals: Mapped[list["Withdrawal"]] = relationship(
        "Withdrawal",
        back_populates="user",
        lazy="selectin",
        order_by="Withdrawal.created_at.desc()",
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="user",
        lazy="selectin",
        order_by="Order.created_at.desc()",
    )

    # trades: Mapped[list["Trade"]] = relationship(
    #     "Trade",
    #     back_populates="user",
    #     lazy="selectin",
    # )

    bank_accounts: Mapped[list["BankAccount"]] = relationship(
        "BankAccount",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Trade.created_at.desc()",
    )

    buy_trades: Mapped[list["Trade"]] = relationship(
        "Trade",
        foreign_keys="Trade.buyer_user_id",
        back_populates="buyer",
        lazy="selectin",
    )

    sell_trades: Mapped[list["Trade"]] = relationship(
        "Trade",
        foreign_keys="Trade.seller_user_id",
        back_populates="seller",
        lazy="selectin",
    )