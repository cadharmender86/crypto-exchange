"""
Exchange Settings Model

Stores dynamic business configuration for BitNova Exchange.
"""

import uuid

from sqlalchemy import Boolean, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import SettingValueType
from app.models.base import Base


class ExchangeSetting(Base):
    __tablename__ = "exchange_settings"

    __table_args__ = (
        Index("idx_exchange_settings_public", "is_public"),
        Index("idx_exchange_settings_type", "value_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    value_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=SettingValueType.STRING,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ExchangeSetting key='{self.key}' value='{self.value}'>"