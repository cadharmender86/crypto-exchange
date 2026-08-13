from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.wallet import Wallet
from app.models.wallet_address import WalletAddress


class WalletAddressService:

    @staticmethod
    async def create_address(
        db: AsyncSession,
        *,
        wallet_id: UUID,
        user_id: UUID,
        asset_id: UUID,
        network: str,
        address: str,
        address_type: str = "DEPOSIT",
    ) -> WalletAddress:

        # Verify wallet belongs to the authenticated user.
        wallet_result = await db.execute(
            select(Wallet).where(
                Wallet.id == wallet_id,
                Wallet.user_id == user_id,
            )
        )

        wallet = wallet_result.scalar_one_or_none()

        if wallet is None:
            raise ValueError("Wallet not found")

        if wallet.status != "ACTIVE":
            raise ValueError("Wallet is not active")

        # Verify asset exists and is active.
        asset_result = await db.execute(
            select(Asset).where(
                Asset.id == asset_id,
            )
        )

        asset = asset_result.scalar_one_or_none()

        if asset is None:
            raise ValueError("Asset not found")

        if not asset.is_active:
            raise ValueError("Asset is not active")

        if not asset.deposit_enabled:
            raise ValueError("Deposits are disabled for this asset")

        # Normalize values.
        network = network.strip().upper()
        address = address.strip()
        address_type = address_type.strip().upper()

        if not network:
            raise ValueError("Network is required")

        if not address:
            raise ValueError("Address is required")

        if not address_type:
            raise ValueError("Address type is required")

        # Prevent duplicate address for the same network.
        existing_result = await db.execute(
            select(WalletAddress).where(
                WalletAddress.network == network,
                WalletAddress.address == address,
            )
        )

        existing = existing_result.scalar_one_or_none()

        if existing is not None:
            raise ValueError(
                "Blockchain address already exists"
            )

        wallet_address = WalletAddress(
            wallet_id=wallet_id,
            asset_id=asset_id,
            network=network,
            address=address,
            address_type=address_type,
            status="ACTIVE",
        )

        db.add(wallet_address)

        try:
            await db.commit()
            await db.refresh(wallet_address)
        except IntegrityError:
            await db.rollback()
            raise ValueError(
                "Blockchain address already exists"
            )
        except Exception:
            await db.rollback()
            raise

        return wallet_address

    @staticmethod
    async def list_addresses(
        db: AsyncSession,
        *,
        wallet_id: UUID,
        user_id: UUID,
    ) -> list[WalletAddress]:

        wallet_result = await db.execute(
            select(Wallet).where(
                Wallet.id == wallet_id,
                Wallet.user_id == user_id,
            )
        )

        wallet = wallet_result.scalar_one_or_none()

        if wallet is None:
            raise ValueError("Wallet not found")

        result = await db.execute(
            select(WalletAddress)
            .where(
                WalletAddress.wallet_id == wallet_id
            )
            .order_by(
                WalletAddress.created_at.desc()
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def get_address(
        db: AsyncSession,
        *,
        wallet_id: UUID,
        address_id: UUID,
        user_id: UUID,
    ) -> WalletAddress:

        wallet_result = await db.execute(
            select(Wallet).where(
                Wallet.id == wallet_id,
                Wallet.user_id == user_id,
            )
        )

        wallet = wallet_result.scalar_one_or_none()

        if wallet is None:
            raise ValueError("Wallet not found")

        result = await db.execute(
            select(WalletAddress).where(
                WalletAddress.id == address_id,
                WalletAddress.wallet_id == wallet_id,
            )
        )

        wallet_address = result.scalar_one_or_none()

        if wallet_address is None:
            raise ValueError("Wallet address not found")

        return wallet_address