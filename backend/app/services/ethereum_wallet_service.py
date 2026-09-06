from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.blockchains.wallets.ethereum_provider import EthereumWalletProvider
from app.models.wallet_address import WalletAddress


class EthereumWalletService:
    """
    Allocates deterministic Ethereum deposit addresses.
    """

    NETWORK = "ETHEREUM_SEPOLIA"

    @classmethod
    async def allocate_deposit_address(
        cls,
        db: AsyncSession,
        *,
        wallet_id,
        user_id,
        asset_id,
    ) -> WalletAddress:

        existing = await db.execute(
            select(WalletAddress).where(
                WalletAddress.user_id == user_id,
                WalletAddress.network == cls.NETWORK,
                WalletAddress.status == "ACTIVE",
            )
        )

        wallet_address = existing.scalar_one_or_none()

        if wallet_address:
            return wallet_address

        result = await db.execute(
            select(
                func.coalesce(
                    func.max(WalletAddress.derivation_index),
                    -1,
                )
            ).where(
                WalletAddress.network == cls.NETWORK
            )
        )

        next_index = result.scalar_one() + 1

        provider = EthereumWalletProvider()

        wallet = await provider.generate_wallet(next_index)

        wallet_address = WalletAddress(
            wallet_id=wallet_id,
            user_id=user_id,
            asset_id=asset_id,
            network=cls.NETWORK,
            address=wallet["address"].lower(),
            derivation_index=next_index,
            address_type="DEPOSIT",
            status="ACTIVE",
        )

        db.add(wallet_address)

        await db.flush()
        await db.refresh(wallet_address)

        return wallet_address