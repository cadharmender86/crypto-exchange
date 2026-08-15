from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class KYCResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    user_email: EmailStr
    status: str
    document_type: str | None = None
    document_reference: str | None = None
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    reviewed_by_admin_id: UUID | None = None
    rejection_reason: str | None = None
    created_at: datetime
    updated_at: datetime


class KYCListResponse(BaseModel):
    items: list[KYCResponse]
    page: int
    page_size: int
    total: int


class KYCReviewRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)
