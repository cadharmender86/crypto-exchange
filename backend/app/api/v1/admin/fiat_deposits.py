from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.admin_auth import require_permission
from app.core.database import get_db
from app.models.admin import AdminUser
from app.models.fiat_deposit import FiatDeposit, FiatDepositStatus
from app.schemas.fiat_deposit import (
    ApproveDepositResponse,
    FiatDepositListResponse,
    FiatDepositResponse,
    RejectDepositRequest,
    RejectDepositResponse,
)
from app.services.admin_fiat_deposit_service import AdminFiatDepositService

router = APIRouter(
    prefix="/fiat/deposits",
    tags=["Admin Fiat Deposits"],
)

@router.get(
    "",
    response_model=FiatDepositListResponse,
)
async def list_fiat_deposits(
    status_filter: FiatDepositStatus | None = Query(
        default=None,
        alias="status",
    ),
    utr_number: str | None = Query(default=None),
    user_id: UUID | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(require_permission("DEPOSIT_READ")),
):
    query = select(FiatDeposit)

    if status_filter:
        query = query.where(FiatDeposit.status == status_filter)

    if utr_number:
        query = query.where(
            FiatDeposit.utr_number.ilike(f"%{utr_number.strip().upper()}%")
        )

    if user_id:
        query = query.where(FiatDeposit.user_id == user_id)

    total = await db.scalar(
        select(func.count()).select_from(query.subquery())
    )

    deposits = await db.scalars(
        query.order_by(FiatDeposit.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    return FiatDepositListResponse(
        items=list(deposits),
        total=total or 0,
    )

@router.get(
    "/{deposit_id}",
    response_model=FiatDepositResponse,
)
async def get_fiat_deposit(
    deposit_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(require_permission("DEPOSIT_READ")),
):
    deposit = await db.get(FiatDeposit, deposit_id)

    if deposit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found.",
        )

    return deposit

@router.post(
    "/{deposit_id}/approve",
    response_model=ApproveDepositResponse,
)
async def approve_fiat_deposit(
    deposit_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_permission("DEPOSIT_APPROVE")),
):
    service = AdminFiatDepositService(db)

    try:
        deposit = await service.approve(
            deposit_id=deposit_id,
            admin_user_id=admin.id,
        )

        await db.commit()

        return ApproveDepositResponse(deposit=deposit)

    except ValueError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

@router.post(
    "/{deposit_id}/reject",
    response_model=RejectDepositResponse,
)
async def reject_fiat_deposit(
    deposit_id: UUID,
    request: RejectDepositRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_permission("DEPOSIT_REJECT")),
):
    service = AdminFiatDepositService(db)

    try:
        deposit = await service.reject(
            deposit_id=deposit_id,
            admin_user_id=admin.id,
            rejection_reason=request.rejection_reason,
        )

        await db.commit()

        return RejectDepositResponse(deposit=deposit)

    except ValueError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )    