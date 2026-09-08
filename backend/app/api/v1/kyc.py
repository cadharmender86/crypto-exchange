from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user
from app.schemas.kyc import (
    PersonalInfoRequest,
    PersonalInfoResponse,
)
from app.services.kyc_service import KYCService
# from app.api.dependencies.auth import get_current_user

router = APIRouter()


@router.get(
    "/profile",
    response_model=PersonalInfoResponse,
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await KYCService.get_profile(
        db,
        current_user.id,
    )

    return profile


@router.put(
    "/personal-info",
    response_model=PersonalInfoResponse,
)
async def save_personal_info(
    payload: PersonalInfoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await KYCService.save_personal_info(
        db,
        current_user.id,
        payload,
    )

    return profile