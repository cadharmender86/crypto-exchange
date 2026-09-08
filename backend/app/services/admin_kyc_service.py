from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime, timezone

from app.models.enums import DocumentStatus,KYCStatus
from app.models.kyc_document import KYCDocument
from app.models.kyc_profile import KYCProfile


class AdminKYCService:

    @staticmethod
    async def get_queue(db):

        result = await db.execute(
            select(KYCProfile)
            .options(selectinload(KYCProfile.user))
            .where(
                KYCProfile.kyc_status.in_(
                    [
                        KYCStatus.SUBMITTED,
                        KYCStatus.UNDER_REVIEW,
                    ]
                )
            )
            .order_by(KYCProfile.submitted_at.desc())
        )

        profiles = result.scalars().all()

        return [
            {
                "user_id": profile.user_id,
                "email": profile.user.email,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "country": profile.country,
                "kyc_status": profile.kyc_status,
                "submitted_at": profile.submitted_at,
            }
            for profile in profiles
        ]

    @staticmethod
    async def get_kyc_detail(
        db,
        user_id: UUID,
    ):
        result = await db.execute(
            select(KYCProfile)
            .options(
                selectinload(KYCProfile.user),
                selectinload(KYCProfile.documents),
            )
            .where(KYCProfile.user_id == user_id)
        )

        profile = result.scalar_one_or_none()

        if profile is None:
            return None

        return {
            "user_id": profile.user_id,
            "email": profile.user.email,
            "kyc_status": profile.kyc_status,

            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "date_of_birth": profile.date_of_birth,
            "nationality": profile.nationality,

            "country": profile.country,
            "state": profile.state,
            "city": profile.city,

            "address_line1": profile.address_line1,
            "address_line2": profile.address_line2,
            "postal_code": profile.postal_code,

            "submitted_at": profile.submitted_at,
            "verified_at": profile.verified_at,
            "rejection_reason": profile.rejection_reason,

            "documents": [
                {
                    "id": doc.id,
                    "document_type": doc.document_type,
                    "status": doc.status,
                    "file_name": doc.file_name,
                    "storage_path": doc.storage_path,
                    "uploaded_at": doc.uploaded_at,
                    "rejection_reason": doc.rejection_reason,
                }
                for doc in profile.documents
            ],
        }

    @staticmethod
    async def approve_kyc(
        db,
        user_id,
        admin_user,
    ):
        result = await db.execute(
            select(KYCProfile).where(
                KYCProfile.user_id == user_id
            )
        )

        profile = result.scalar_one_or_none()

        if profile is None:
            return None

        if profile.kyc_status == KYCStatus.APPROVED:
            raise ValueError("KYC already approved.")

        profile.kyc_status = KYCStatus.APPROVED
        profile.verified_at = datetime.now(timezone.utc)
        profile.verified_by = admin_user.id
        profile.rejection_reason = None

        docs = await db.execute(
            select(KYCDocument).where(
                KYCDocument.user_id == user_id
            )
        )

        for document in docs.scalars():
            document.status = DocumentStatus.APPROVED
            document.rejection_reason = None
            document.verified_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(profile)

        return profile

    @staticmethod
    async def reject_kyc(
        db,
        user_id,
        admin_user,
        reason: str,
    ):
        result = await db.execute(
            select(KYCProfile).where(
                KYCProfile.user_id == user_id
            )
        )

        profile = result.scalar_one_or_none()

        if profile is None:
            return None

        if profile.kyc_status == KYCStatus.REJECTED:
            raise ValueError("KYC already rejected.")

        profile.kyc_status = KYCStatus.REJECTED
        profile.rejection_reason = reason
        profile.verified_at = datetime.now(timezone.utc)
        profile.verified_by = admin_user.id

        docs_result = await db.execute(
            select(KYCDocument).where(
                KYCDocument.user_id == user_id
            )
        )

        for document in docs_result.scalars():
            document.status = DocumentStatus.REJECTED
            document.rejection_reason = reason
            document.verified_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(profile)

        return profile