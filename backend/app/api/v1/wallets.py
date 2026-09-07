from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from app.models.asset import Asset
from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.wallet import (
    WalletCreateRequest,
    WalletResponse,
)
from app.services.wallet_service import WalletService
from app.schemas.ledger import LedgerTransactionResponse
from app.services.ledger_service import LedgerService
from app.schemas.wallet_dashboard import WalletDashboardResponse
# from app.schemas.wallet_address import WalletAddressGenerateRequest
# from app.services.wallet_address_service import WalletAddressService



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
    "/dashboard",
    response_model=WalletDashboardResponse,
)
async def get_wallet_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await WalletService.get_wallet_dashboard(
        db=db,
        user_id=current_user.id,
    )

@router.get(
    "/transactions",
    response_model=list[LedgerTransactionResponse],
)
async def get_wallet_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await LedgerService.list_user_transactions(
        db=db,
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

# @router.post("/receive/generate")
# async def generate_receive_address(
#     request: WalletAddressGenerateRequest,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     try:
#         wallet = await WalletService.get_user_wallet(
#             db=db,
#             user_id=current_user.id,
#         )

#         if wallet is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Wallet not found",
#             )

#         asset_result = await db.execute(
#             select(Asset).where(
#                 Asset.symbol == request.asset.upper()
#             )
#         )

#         asset = asset_result.scalar_one_or_none()

#         if asset is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Asset not found",
#                 )

#         if not asset.is_active:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Asset is not active",
#             )

#         if not asset.deposit_enabled:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Deposits are disabled for this asset",
#             )

#         wallet_address = await WalletAddressService.get_or_create_address(
#             db=db,
#             wallet_id=wallet.id,
#             user_id=current_user.id,
#             asset_id=asset.id,
#             network=request.network,
#         )

#         await db.commit()

#         return {
#             "asset": request.asset,
#             "network": request.network,
#             "address": wallet_address.address,
#             "derivation_index": wallet_address.derivation_index,
#         }

#     except ValueError as exc:
#         await db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(exc),
#         )

# @router.get("/receive")
# async def get_receive_address(
#     network: str,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db),
# ):
#     wallet = await WalletService.get_user_wallet(
#         db=db,
#         user_id=current_user.id,
#     )

#     if wallet is None:
#         raise HTTPException(
#             status_code=404,
#             detail="Wallet not found",
#         )

#     addresses = await WalletAddressService.list_addresses(
#         db=db,
#         wallet_id=wallet.id,
#         user_id=current_user.id,
#     )

#     for address in addresses:
#         if address.network == network.upper():
#             return {
#                 "generated": True,
#                 "address": address.address,
#                 "network": address.network,
#                 "derivation_index": address.derivation_index,
#             }

#     return {
#         "generated": False,
#         "network": network.upper(),
#     }    