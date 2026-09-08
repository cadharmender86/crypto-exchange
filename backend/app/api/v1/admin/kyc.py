from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.admin_kyc import AdminKYCQueueItem
from app.services.admin_kyc_service import AdminKYCService

router = APIRouter(prefix="/kyc", tags=["Admin KYC"])


@router.get(
    "/queue",
    response_model=list[AdminKYCQueueItem],
)
async def kyc_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await AdminKYCService.get_queue(db)