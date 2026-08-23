from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    decimal_places: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    deposit_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    withdrawal_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    trading_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
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

    accounts: Mapped[list["Account"]] = relationship(
        "Account",
        back_populates="asset",
        lazy="selectin",
    )

    wallet_addresses: Mapped[list["WalletAddress"]] = relationship(
        "WalletAddress",
        back_populates="asset",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    deposits: Mapped[list["Deposit"]] = relationship(
        "Deposit",
        back_populates="asset",
        lazy="selectin",
    )

    withdrawals: Mapped[list["Withdrawal"]] = relationship(
        "Withdrawal",
        back_populates="asset",
        lazy="selectin",
    )

    base_orders: Mapped[list["Order"]] = relationship(
        "Order",
        foreign_keys="Order.base_asset_id",
        back_populates="base_asset",
        lazy="selectin",
    )

    quote_orders: Mapped[list["Order"]] = relationship(
        "Order",
        foreign_keys="Order.quote_asset_id",
        back_populates="quote_asset",
        lazy="selectin",
    )

    base_trades: Mapped[list["Trade"]] = relationship(
        "Trade",
        foreign_keys="Trade.base_asset_id",
        back_populates="base_asset",
        lazy="selectin",
    )

    quote_trades: Mapped[list["Trade"]] = relationship(
        "Trade",
        foreign_keys="Trade.quote_asset_id",
        back_populates="quote_asset",
        lazy="selectin",
    )