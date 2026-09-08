from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class KYCDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_type: str
    status: str
    file_name: str
    uploaded_at: datetime | None
    verified_at: datetime | None
    rejection_reason: str | None


class KYCUploadResponse(BaseModel):
    message: str
    document: KYCDocumentResponse