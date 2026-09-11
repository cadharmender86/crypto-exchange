"""Trading Pair Model for BitNova Exchange"""

# from uuid import uuid4
import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Index,
    DateTime,
    func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.constants import TradingPairStatus
from app.models.base import Base


class TradingPair(Base):
    __tablename__ = "trading_pairs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    base_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
    )

    quote_asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
    )   

    pair_code: Mapped[str] = mapped_column(
        String(20), unique=True,
    )
    
    display_name: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    price_precision: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
    )

    quantity_precision: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=8,
    )

    tick_size: Mapped[Decimal] = mapped_column(
        Numeric(24, 12),
        nullable=False,
    )

    step_size: Mapped[Decimal] = mapped_column(
        Numeric(24, 12),
        nullable=False,
    )

    minimum_order_quantity: Mapped[Decimal] = mapped_column(
        Numeric(24, 12),
        nullable=False,
    )

    maximum_order_quantity: Mapped[Decimal] = mapped_column(
        Numeric(24, 12),
        nullable=False,
    )

    minimum_order_value: Mapped[Decimal] = mapped_column(
        Numeric(24, 12),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=TradingPairStatus.ACTIVE,
    )

    is_visible: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    is_default = Column(Boolean, default=False)

    base_asset: Mapped["Asset"] = relationship(
        foreign_keys=[base_asset_id],
        lazy="joined",
    )

    quote_asset: Mapped["Asset"] = relationship(
        foreign_keys=[quote_asset_id],
        lazy="joined",
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

    __table_args__ = (
        UniqueConstraint(
            "base_asset_id",
            "quote_asset_id",
            name="uq_trading_pair",
        ),
        Index("idx_pair_code", "pair_code"),
        Index("idx_pair_status", "status"),
        Index(
            "idx_pair_visible",
            "is_visible",
        ),
    )

    def __repr__(self) -> str:
        return f"<TradingPair pair='{self.pair_code}' status='{self.status}'>"