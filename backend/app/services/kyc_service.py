from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import KYCStatus
from app.models.kyc_profile import KYCProfile
from app.schemas.kyc import PersonalInfoRequest


class KYCService:
    """Business logic for customer KYC."""

    @staticmethod
    async def get_or_create_profile(
        db: AsyncSession,
        user_id: UUID,
    ) -> KYCProfile:
        """Return user's KYC profile or create one."""

        result = await db.execute(
            select(KYCProfile).where(KYCProfile.user_id == user_id)
        )

        profile = result.scalar_one_or_none()

        if profile:
            return profile

        profile = KYCProfile(
            user_id=user_id,
            kyc_status=KYCStatus.NOT_STARTED,
        )

        db.add(profile)
        await db.flush()

        return profile

    @staticmethod
    async def get_profile(
        db: AsyncSession,
        user_id: UUID,
    ) -> KYCProfile:
        """Return KYC profile (creates empty profile if needed)."""

        return await KYCService.get_or_create_profile(db, user_id)

    @staticmethod
    async def save_personal_info(
        db: AsyncSession,
        user_id: UUID,
        payload: PersonalInfoRequest,
    ) -> KYCProfile:
        """Create or update customer's personal information."""

        profile = await KYCService.get_or_create_profile(db, user_id)

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

        # First save moves profile into DRAFT state.
        if profile.kyc_status == KYCStatus.NOT_STARTED:
            profile.kyc_status = KYCStatus.DRAFT

        await db.commit()
        await db.refresh(profile)

        return profile