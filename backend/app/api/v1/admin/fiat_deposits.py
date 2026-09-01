from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.admin_auth import require_permission
from app.core.database import get_db
from app.models.admin import AdminUser, AuditLog
from app.models.fiat_deposit import FiatDeposit, FiatDepositStatus
from app.models.user import User
from app.schemas.admin import (
    FiatDepositListItem,
    FiatDepositListResponse,
    FiatDepositDetailResponse,
    ApproveDepositRequest,
    ApproveDepositResponse,
    RejectDepositRequest,
    RejectDepositResponse,
)
from app.services.admin_fiat_deposit_service import AdminFiatDepositService

router = APIRouter(
    prefix="/fiat-deposits",
    tags=["Admin Fiat Deposits"],
)

@router.get(
    "",
    response_model=FiatDepositListResponse,
)
async def list_fiat_deposits(
    status_filter: FiatDepositStatus | None = Query(None, alias="status"),
    utr_number: str | None = Query(None),
    user_id: UUID | None = Query(None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(require_permission("FIAT_DEPOSIT_READ")),
):
    query = (
        select(FiatDeposit)
        .options(
            selectinload(FiatDeposit.user),
            selectinload(FiatDeposit.bank_account),
        )
        .order_by(FiatDeposit.created_at.desc())
    )

    if status_filter:
        query = query.where(FiatDeposit.status == status_filter)

    if utr_number:
        query = query.where(
            FiatDeposit.utr_number.ilike(f"%{utr_number.strip().upper()}%")
        )

    if user_id:
        query = query.where(FiatDeposit.user_id == user_id)

    # Total records before pagination
    total = await db.scalar(
        select(func.count()).select_from(query.subquery())
    )

    deposits = (
        await db.scalars(
            query.limit(limit).offset(offset)
        )
    ).all()

    return FiatDepositListResponse(
        items=[
            FiatDepositListItem(
                id=d.id,
                user_name=d.user.email if d.user else "Unknown User",
                user_email=d.user.email if d.user else "",
                bank_name=d.bank_account.bank_name if d.bank_account else "N/A",
                utr_number=d.utr_number,
                amount=d.amount,
                currency=d.currency,
                status=d.status.value,
                created_at=d.created_at,
            )
            for d in deposits
        ],
        total=total or 0,
    )

@router.get(
    "/{deposit_id}",
    response_model=FiatDepositDetailResponse,
)
async def get_fiat_deposit(
    deposit_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(require_permission("FIAT_DEPOSIT_READ")),
):
    deposit = await db.scalar(
        select(FiatDeposit)
        .options(
            selectinload(FiatDeposit.user),
            selectinload(FiatDeposit.bank_account),
        )
        .where(FiatDeposit.id == deposit_id)
    )

    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")

    return FiatDepositDetailResponse(
        id=deposit.id,
        user_name=d.user.email if deposit.user else "Unknown User",
        user_email=deposit.user.email if deposit.user else "",
        bank_name=deposit.bank_account.bank_name if deposit.bank_account else "N/A",
        account_holder_name=deposit.bank_account.account_holder_name if deposit.bank_account else "N/A",
        account_number=deposit.bank_account.account_number if deposit.bank_account else "N/A",
        ifsc_code=deposit.bank_account.ifsc_code if deposit.bank_account else "N/A",
        utr_number=deposit.utr_number,
        amount=deposit.amount,
        currency=deposit.currency,
        status=deposit.status.value,
        remarks=deposit.remarks,
        rejection_reason=deposit.rejection_reason,
        approved_at=deposit.approved_at,
        created_at=deposit.created_at,
    )

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

        return ApproveDepositResponse(
            success=True,
            message="Fiat Deposit approved successfully",
            deposit_id=deposit.id,
            status=deposit.status.value if hasattr(deposit.status, "value") else str(deposit.status),
        )

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

        return RejectDepositResponse(
            success=True,
            message="Fiat Deposit rejected successfully",
            deposit_id=deposit.id,
            status=deposit.status.value if hasattr(deposit.status, "value") else str(deposit.status),
        )

    except ValueError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )    