from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.deposit import Deposit
from app.schemas.deposit import (
    DepositCreate,
    DepositResponse,
)
from app.services.deposit_service import DepositService


router = APIRouter(
    prefix="/deposits",
    tags=["Deposits"],
)


@router.post(
    "",
    response_model=DepositResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_deposit(
    request: DepositCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        deposit = (
            await DepositService.create_pending_deposit(
                db,
                user_id=current_user.id,
                wallet_address_id=request.wallet_address_id,
                asset_id=request.asset_id,
                network=request.network,
                blockchain_tx_hash=request.blockchain_tx_hash,
                amount=request.amount,
            )
        )

        await db.commit()
        await db.refresh(deposit)

        return deposit

    except ValueError as exc:
        await db.rollback()

        detail = str(exc)

        if (
            detail
            == "Blockchain transaction already belongs "
            "to another user"
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=detail,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    except Exception:
        await db.rollback()
        raise


@router.get(
    "",
    response_model=list[DepositResponse],
)
async def list_my_deposits(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Deposit)
        .where(
            Deposit.user_id == current_user.id
        )
        .order_by(
            Deposit.created_at.desc()
        )
    )

    return list(result.scalars().all())


@router.get(
    "/{deposit_id}",
    response_model=DepositResponse,
)
async def get_my_deposit(
    deposit_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Deposit)
        .where(
            Deposit.id == deposit_id,
            Deposit.user_id == current_user.id,
        )
    )

    deposit = result.scalar_one_or_none()

    if deposit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found",
        )

    return deposit