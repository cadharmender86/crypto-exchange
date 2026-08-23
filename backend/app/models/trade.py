from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    buyer_user_id = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    seller_user_id = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    base_asset_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quote_asset_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    buy_order_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    sell_order_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    
    price: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    quote_amount: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    buy_order = relationship(
        "Order",
        foreign_keys="Trade.buy_order_id",
        back_populates="buy_trades",
    )

    sell_order = relationship(
        "Order",
        foreign_keys="Trade.sell_order_id",
        back_populates="sell_trades",
    )

    buyer = relationship(
        "User",
        foreign_keys=[buyer_user_id],
        back_populates="buy_trades",
    )

    seller = relationship(
        "User",
        foreign_keys=[seller_user_id],
        back_populates="sell_trades",
    )

    base_asset: Mapped["Asset"] = relationship(
        "Asset",
        foreign_keys=[base_asset_id],
        back_populates="base_trades",
    )

    quote_asset: Mapped["Asset"] = relationship(
        "Asset",
        foreign_keys=[quote_asset_id],
        back_populates="quote_trades",
    )