from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class WalletAddress(Base):
    __tablename__ = "wallet_addresses"

    __table_args__ = (
        UniqueConstraint(
            "wallet_id",
            "asset_id",
            "network",
            name="uq_wallet_address_asset_network",
        ),
        UniqueConstraint(
            "network",
            "address",
            name="uq_wallet_address_network_address",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    wallet_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "wallets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    asset_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "assets.id",
        ),
        nullable=False,
        index=True,
    )

    network: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    address_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="DEPOSIT",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
        index=True,
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

    user = relationship(
        "User",
        back_populates="wallet_addresses",
    )

    asset = relationship(
        "Asset",
        back_populates="wallet_addresses",
    )

    deposits = relationship(
        "Deposit",
        back_populates="wallet_address",
        lazy="selectin",
    )