from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func, Index, Enum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.core.constants import (
    OrderSide,
    OrderStatus,
    OrderType,
    TimeInForce,
)


class Order(Base):
    __tablename__ = "orders"

    __table_args__ = (
        Index(
            "idx_order_book_lookup",
            "trading_pair_id",
            "side",
            "status",
            "price",
            "created_at",
        ),

        Index(
            "idx_order_user_status",
            "user_id",
            "status",
        ),   
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # base_asset_id: Mapped[UUID] = mapped_column(
    #     PGUUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False, index=True
    # )
    # quote_asset_id: Mapped[UUID] = mapped_column(
    #     PGUUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False, index=True
    # )
    # client_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    side: Mapped[str] = mapped_column(String(4), nullable=False, index=True)
    order_type: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN", index=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(38, 18), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    # filled_quantity: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False, default=Decimal("0"))
    remaining_quantity: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    # average_execution_price: Mapped[Decimal | None] = mapped_column(Numeric(38, 18), nullable=True)
    fee_amount: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False, default=Decimal("0"))
    fee_asset_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    # cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # -----------------------------
    # Relationships
    # -----------------------------

    user = relationship(
        "User",
        back_populates="orders",
    )

    base_asset = relationship(
        "Asset",
        foreign_keys=[base_asset_id],
        back_populates="base_orders",
    )

    quote_asset = relationship(
        "Asset",
        foreign_keys=[quote_asset_id],
        back_populates="quote_orders"
    )

    buy_trades = relationship(
        "Trade",
        foreign_keys="Trade.buy_order_id",
        back_populates="buy_order",
        lazy="selectin"
    )

    sell_trades = relationship(
        "Trade",
        foreign_keys="Trade.sell_order_id",
        back_populates="sell_order",
        lazy="selectin"
    )

    # -------------------------
    # Trading Pair
    # -------------------------
    trading_pair_id: Mapped[UUID] = mapped_column(
        ForeignKey("trading_pairs.id"),
        nullable=False,
        index=True,
    )

    trading_pair = relationship(
        "TradingPair",
        back_populates="orders",
    )


    # -------------------------
    # Side / Type / Status
    # -------------------------
    side: Mapped[OrderSide] = mapped_column(
        Enum(OrderSide),
        nullable=False,
    )

    order_type: Mapped[OrderType] = mapped_column(
        Enum(OrderType),
        nullable=False,
        default=OrderType.LIMIT,
    )

    time_in_force: Mapped[TimeInForce] = mapped_column(
        Enum(TimeInForce),
        nullable=False,
        default=TimeInForce.GTC,
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        nullable=False,
        default=OrderStatus.NEW,
    )

    # -------------------------
    # Pricing
    # -------------------------
    price: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 8),
        nullable=True,
    )

    average_price: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        default=0,
        nullable=False,
    )

    quote_amount: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        default=0,
        nullable=False,
    )

    # -------------------------
    # Quantities
    # -------------------------
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )

    executed_quantity: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        default=0,
        nullable=False,
    )

    remaining_quantity: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        nullable=False,
    )


    # -------------------------
    # Fees
    # -------------------------
    fee_asset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("assets.id"),
    )

    fee_amount: Mapped[Decimal] = mapped_column(
        Numeric(24, 8),
        default=0,
        nullable=False,
    )

    fee_asset = relationship(
        "Asset",
        foreign_keys=[fee_asset_id],
        lazy="joined",
    )


    # -------------------------
    # Cancellation
    # -------------------------
    cancel_reason: Mapped[str | None] = mapped_column(
        String(100),
    )

