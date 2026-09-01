from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.admin_auth import require_permission
from app.core.database import get_db
from app.models.admin import AdminUser
from app.models.asset import Asset
from app.models.fiat_deposit import FiatDeposit
from app.models.kyc import KYCRecord, KYCStatus
from app.models.user import User
from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.schemas.admin import AdminDashboardResponse

router = APIRouter(
    prefix="/dashboard",
    tags=["Admin Dashboard"],
)


@router.get("", response_model=AdminDashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(require_permission("DASHBOARD_READ")),
):
    total_users = await db.scalar(
        select(func.count(User.id))
    ) or 0

    active_users = await db.scalar(
        select(func.count(User.id)).where(User.is_active.is_(True))
    ) or 0

    verified_users = await db.scalar(
        select(func.count(User.id)).where(User.is_verified.is_(True))
    ) or 0

    pending_kyc = await db.scalar(
        select(func.count(KYCRecord.id)).where(
            KYCRecord.status.in_(
                [
                    KYCStatus.PENDING,
                    KYCStatus.UNDER_REVIEW,
                    KYCStatus.REQUIRES_REVERIFICATION,
                ]
            )
        )
    ) or 0

    total_deposits = await db.scalar(
        select(func.count(FiatDeposit.id))
    ) or 0

    total_withdrawals = await db.scalar(
        select(func.count(Withdrawal.id))
    ) or 0

    pending_withdrawals = await db.scalar(
        select(func.count(Withdrawal.id)).where(
            Withdrawal.status == WithdrawalStatus.PENDING
        )
    ) or 0

    active_assets = await db.scalar(
        select(func.count(Asset.id)).where(
            Asset.is_active.is_(True)
        )
    ) or 0

    return AdminDashboardResponse(
        total_users=total_users,
        active_users=active_users,
        verified_users=verified_users,
        pending_kyc=pending_kyc,
        total_deposits=total_deposits,
        total_withdrawals=total_withdrawals,
        pending_withdrawals=pending_withdrawals,
        active_assets=active_assets,
    )