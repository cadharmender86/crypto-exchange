from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Order(Base):
    __tablename__ = "orders"

    __table_args__ = (
        UniqueConstraint("user_id", "client_order_id", name="uq_orders_user_client_order_id"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    base_asset_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quote_asset_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    client_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    side: Mapped[str] = mapped_column(String(4), nullable=False, index=True)
    order_type: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN", index=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(38, 18), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    filled_quantity: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False, default=Decimal("0"))
    remaining_quantity: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False)
    average_execution_price: Mapped[Decimal | None] = mapped_column(Numeric(38, 18), nullable=True)
    fee_amount: Mapped[Decimal] = mapped_column(Numeric(38, 18), nullable=False, default=Decimal("0"))
    fee_asset_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
