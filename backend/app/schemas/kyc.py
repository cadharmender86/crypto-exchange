from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import KYCStatus


# ============================================================
# Personal Information (Step 4.2)
# ============================================================


class PersonalInfoRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)

    date_of_birth: date

    nationality: str = Field(max_length=100)
    country: str = Field(max_length=100)

    state: str = Field(max_length=100)
    city: str = Field(max_length=100)

    address_line1: str = Field(max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)

    postal_code: str = Field(min_length=6, max_length=10)


class PersonalInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    kyc_status: KYCStatus

    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None

    nationality: str | None = None
    country: str | None = None

    state: str | None = None
    city: str | None = None

    address_line1: str | None = None
    address_line2: str | None = None

    postal_code: str | None = None


# ============================================================
# Customer KYC
# ============================================================


class KYCSubmitRequest(BaseModel):
    document_type: str = Field(min_length=2, max_length=50)
    document_reference: str = Field(min_length=2, max_length=255)
    extra_data: dict | None = None


class KYCUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    status: str
    document_type: str | None = None
    document_reference: str | None = None
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    rejection_reason: str | None = None
    created_at: datetime
    updated_at: datetime


# ============================================================
# Admin KYC
# ============================================================


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
