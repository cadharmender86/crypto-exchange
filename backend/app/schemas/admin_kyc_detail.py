from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import DocumentStatus, DocumentType, KYCStatus


class AdminKYCDocument(BaseModel):
    id: UUID
    document_type: DocumentType
    status: DocumentStatus
    file_name: str
    storage_path: str
    uploaded_at: datetime
    rejection_reason: str | None = None


class AdminKYCDetailResponse(BaseModel):
    user_id: UUID
    email: str

    kyc_status: KYCStatus

    first_name: str | None
    last_name: str | None
    date_of_birth: datetime | None
    nationality: str | None

    country: str | None
    state: str | None
    city: str | None

    address_line1: str | None
    address_line2: str | None
    postal_code: str | None

    submitted_at: datetime | None
    verified_at: datetime | None
    rejection_reason: str | None

    documents: list[AdminKYCDocument]