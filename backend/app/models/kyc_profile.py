from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import KYCStatus


class KYCProfile(TimestampMixin, Base):
    __tablename__ = "kyc_profiles"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    kyc_status: Mapped[KYCStatus] = mapped_column(
        Enum(KYCStatus, name="kyc_status"),
        default=KYCStatus.NOT_STARTED,
        nullable=False,
    )

    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    date_of_birth: Mapped[date | None] = mapped_column(Date)

    nationality: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))

    address_line1: Mapped[str | None] = mapped_column(String(255))
    address_line2: Mapped[str | None] = mapped_column(String(255))
    postal_code: Mapped[str | None] = mapped_column(String(20))

    pan_number: Mapped[str | None] = mapped_column(
        String(10),
        unique=True,
        index=True,
    )

    aadhaar_number_masked: Mapped[str | None] = mapped_column(
        String(20)
    )

    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    verified_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id")
    )

    rejection_reason: Mapped[str | None] = mapped_column(Text)

    # Relationships
    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="kyc_profile",
    )

    documents: Mapped[list["KYCDocument"]] = relationship(
        "KYCDocument",
        back_populates="profile",
        cascade="all, delete-orphan",
        lazy="selectin",
    )