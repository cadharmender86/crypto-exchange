from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.fiat_deposit import FiatDeposit
from app.schemas.fiat_deposit import (
    CreateFiatDepositRequest,
    FiatDepositResponse,
    FiatDepositListResponse,
)
from app.services.fiat_deposit_service import FiatDepositService

router = APIRouter(
    prefix="/fiat/deposits",
    tags=["Fiat Deposits"],
)

@router.post(
    "",
    response_model=FiatDepositResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_fiat_deposit(
    request: CreateFiatDepositRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = FiatDepositService(db)

    try:
        deposit = await service.submit_deposit(
            user_id=user.id,
            bank_account_id=request.bank_account_id,
            amount=request.amount,
            utr_number=request.utr_number,
            remarks=request.remarks,
        )

        await db.commit()
        return deposit

    except (ValueError, PermissionError) as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

@router.get(
    "",
    response_model=FiatDepositListResponse,
)
async def list_my_fiat_deposits(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(FiatDeposit).where(
        FiatDeposit.user_id == user.id
    )

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
async def get_my_fiat_deposit(
    deposit_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deposit = await db.scalar(
        select(FiatDeposit).where(
            FiatDeposit.id == deposit_id,
            FiatDeposit.user_id == user.id,
        )
    )

    if deposit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found.",
        )

    return deposit    