from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class UserSession(UUIDPrimaryKeyMixin, TimestampMixin, Base,):
    __tablename__ = "user_sessions"
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True,)

    refresh_token_hash: Mapped[str] = mapped_column(String(255), nullable=False,)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,)

    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True,)
