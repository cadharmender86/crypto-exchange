from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user, get_db
from app.schemas.wallet_address import (
    WalletAddressCreate,
    WalletAddressResponse,
)
from app.services.wallet_address_service import (
    WalletAddressService,
)
router = APIRouter(
    prefix="/wallets",
    tags=["Wallet Addresses"],
)
@router.post(
    "/{wallet_id}/addresses",
    response_model=WalletAddressResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_wallet_address(
    wallet_id: UUID,
    request: WalletAddressCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await WalletAddressService.create_address(
            db,
            wallet_id=wallet_id,
            user_id=current_user.id,
            asset_id=request.asset_id,
            network=request.network,
            address=request.address,
            address_type=request.address_type,
        )
    except ValueError as exc:
        detail = str(exc)
    if detail == "Blockchain address already exists":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )
@router.get(
    "/{wallet_id}/addresses",
    response_model=list[WalletAddressResponse],
)
async def list_wallet_addresses(
    wallet_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await WalletAddressService.list_addresses(
            db,
            wallet_id=wallet_id,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
@router.get(
    "/{wallet_id}/addresses/{address_id}",
    response_model=WalletAddressResponse,
)
async def get_wallet_address(
    wallet_id: UUID,
    address_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await WalletAddressService.get_address(
            db,
            wallet_id=wallet_id,
            address_id=address_id,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
