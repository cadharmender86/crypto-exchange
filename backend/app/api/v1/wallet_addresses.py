from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from app.models.asset import Asset

from app.api.dependencies import get_current_user, get_db

from app.services.wallet_service import WalletService
from app.schemas.wallet_address import (
    WalletAddressCreate,
    WalletAddressResponse,
    WalletAddressGenerateRequest,
    WalletAddressGenerateResponse,
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

@router.post(
        "/receive/generate",
        response_model=WalletAddressGenerateResponse,
    )
async def generate_receive_address(
    request: WalletAddressGenerateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        wallet = await WalletService.get_user_wallet(
            db=db,
            user_id=current_user.id,
        )

        if wallet is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found",
            )

        asset_result = await db.execute(
            select(Asset).where(
                Asset.symbol == request.asset.upper()
            )
        )

        asset = asset_result.scalar_one_or_none()

        if asset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found",
            )

        # Check if this user already has an address on this network
        existing_addresses = await WalletAddressService.list_addresses(
            db=db,
            wallet_id=wallet.id,
            user_id=current_user.id,
        )

        existing_address = next(
            (
                addr
                for addr in existing_addresses
                if addr.network == request.network.upper()
                and addr.status == "ACTIVE"
            ),
            None,
        )

        wallet_address = await WalletAddressService.get_or_create_address(
            db=db,
            wallet_id=wallet.id,
            user_id=current_user.id,
            asset_id=asset.id,
            network=request.network,
        )

        await db.commit()

        return WalletAddressGenerateResponse(
            asset=request.asset.upper(),
            network=wallet_address.network,
            address=wallet_address.address,
            derivation_index=wallet_address.derivation_index,
            newly_generated=existing_address is None,
        )

    except ValueError as exc:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

@router.get("/receive")
async def get_receive_address(
    network: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    wallet = await WalletService.get_user_wallet(
        db=db,
        user_id=current_user.id,
    )

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )

    addresses = await WalletAddressService.list_addresses(
        db=db,
        wallet_id=wallet.id,
        user_id=current_user.id,
    )

    for address in addresses:
        if (
            address.network == network.upper()
            and address.status == "ACTIVE"
        ):
            return {
                "generated": True,
                "network": address.network,
                "address": address.address,
                "derivation_index": address.derivation_index,
            }

    return {
        "generated": False,
        "network": network.upper(),
    }

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
