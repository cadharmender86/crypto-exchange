from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import DocumentStatus, DocumentType
from app.models.kyc_document import KYCDocument
from app.models.enums import KYCStatus
from app.models.kyc_profile import KYCProfile
from app.schemas.kyc import PersonalInfoRequest
from app.models.user import User
from app.services.storage_service import StorageService


class KYCService:

    @staticmethod
    async def get_profile(
        db: AsyncSession,
        user_id,
    ) -> KYCProfile:

        result = await db.execute(
            select(KYCProfile).where(
                KYCProfile.user_id == user_id
            )
        )

        profile = result.scalar_one_or_none()

        if profile is None:
            profile = KYCProfile(
                user_id=user_id,
                kyc_status=KYCStatus.NOT_STARTED,
            )

            db.add(profile)
            await db.commit()
            await db.refresh(profile)

        return profile

    @staticmethod
    async def save_personal_info(
        db: AsyncSession,
        user_id,
        payload: PersonalInfoRequest,
    ) -> KYCProfile:

        profile = await KYCService.get_profile(db, user_id)

        profile.first_name = payload.first_name
        profile.last_name = payload.last_name
        profile.date_of_birth = payload.date_of_birth
        profile.nationality = payload.nationality
        profile.country = payload.country
        profile.state = payload.state
        profile.city = payload.city
        profile.address_line1 = payload.address_line1
        profile.address_line2 = payload.address_line2
        profile.postal_code = payload.postal_code
        # profile.pan_number = payload.pan_number
        # profile.aadhaar_number_masked = payload.aadhaar_number_masked

        if profile.kyc_status == KYCStatus.NOT_STARTED:
            profile.kyc_status = KYCStatus.DRAFT

        await db.commit()
        await db.refresh(profile)

        return profile

class KYCDocumentService:
    """Upload and manage KYC documents."""

    @staticmethod
    async def upload_document(
        db: AsyncSession,
        user: User,
        file: UploadFile,
        document_type: DocumentType,
    ) -> KYCDocument:

        folder = document_type.value.lower()

        # Save file locally (development)
        try:
            storage_path, file_size = await StorageService.save_kyc_document(
                file=file,
                folder=folder,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            )

        # Check if document already exists
        result = await db.execute(
            select(KYCDocument).where(
                KYCDocument.user_id == user.id,
                KYCDocument.document_type == document_type,
            )
        )

        document = result.scalar_one_or_none()

        if document:
            # Replace existing document
            document.file_name = file.filename
            document.storage_path = storage_path
            document.mime_type = file.content_type or "application/octet-stream"
            document.file_size = file_size
            document.status = DocumentStatus.PENDING
            document.rejection_reason = None
            document.verified_at = None
            document.uploaded_at = datetime.now(timezone.utc)

        else:
            document = KYCDocument(
                user_id=user.id,
                document_type=document_type,
                file_name=file.filename,
                storage_path=storage_path,
                mime_type=file.content_type or "application/octet-stream",
                file_size=file_size,
                status=DocumentStatus.PENDING,
                uploaded_at=datetime.now(timezone.utc),
            )

            db.add(document)

        await db.commit()
        await db.refresh(document)

        return document