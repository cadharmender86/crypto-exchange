from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.withdrawal import Withdrawal
from app.schemas.withdrawal import WithdrawalCreate, WithdrawalResponse
from app.services.withdrawal_service import WithdrawalService


router = APIRouter(
    prefix="/withdrawals",
    tags=["Withdrawals"],
)


@router.post(
    "",
    response_model=WithdrawalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_withdrawal(
    request: WithdrawalCreate,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=8,
        max_length=100,
    ),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        withdrawal = await WithdrawalService.create_pending_withdrawal(
            db,
            user_id=current_user.id,
            asset_id=request.asset_id,
            network=request.network,
            destination_address=request.destination_address,
            amount=request.amount,
            idempotency_key=idempotency_key,
        )
        await db.commit()
        await db.refresh(withdrawal)
        return withdrawal
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[WithdrawalResponse],
)
async def list_my_withdrawals(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Withdrawal)
        .where(Withdrawal.user_id == current_user.id)
        .order_by(Withdrawal.created_at.desc())
    )
    return list(result.scalars().all())


@router.get(
    "/{withdrawal_id}",
    response_model=WithdrawalResponse,
)
async def get_my_withdrawal(
    withdrawal_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Withdrawal).where(
            Withdrawal.id == withdrawal_id,
            Withdrawal.user_id == current_user.id,
        )
    )
    withdrawal = result.scalar_one_or_none()

    if withdrawal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal not found",
        )

    return withdrawal
