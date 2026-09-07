from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import (
    Base,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class EmailOTP(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "email_otps"

    # User who owns this OTP
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Email being verified
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # Store hashed OTP only
    otp_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # REGISTER / RESET_PASSWORD / CHANGE_EMAIL
    purpose: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="REGISTER",
    )

    # Number of failed attempts
    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # OTP expiry (10 minutes)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    # Set after successful verification
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    