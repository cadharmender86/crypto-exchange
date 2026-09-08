from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.enums import KYCStatus
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