from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.wallet import (
    WalletCreateRequest,
    WalletResponse,
)
from app.services.wallet_service import WalletService


router = APIRouter(
    prefix="/wallets",
    tags=["Wallets"],
)


@router.post(
    "",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_wallet(
    request: WalletCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    try:
        wallet = await WalletService.create_wallet(
            db,
            user_id=current_user.id,
            wallet_type=request.wallet_type,
        )

        await db.commit()

        await db.refresh(wallet)

        return wallet

    except ValueError as exc:

        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[WalletResponse],
)
async def list_wallets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    return await WalletService.list_user_wallets(
        db,
        user_id=current_user.id,
    )


@router.get(
    "/{wallet_id}",
    response_model=WalletResponse,
)
async def get_wallet(
    wallet_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    wallet = await WalletService.get_wallet(
        db,
        wallet_id,
    )

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    # Critical authorization check.
    if wallet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    return wallet