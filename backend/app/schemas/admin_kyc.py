from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import KYCStatus


class AdminKYCQueueItem(BaseModel):
    user_id: UUID
    email: str

    first_name: str | None
    last_name: str | None

    country: str | None
    kyc_status: KYCStatus

    submitted_at: datetime | None

    class Config:
        from_attributes = True