from decimal import Decimal
from typing import Any
# from uuid import UUID

# from backend.app.schemas import wallet
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.models.wallet import Wallet
from app.models.wallet_address import WalletAddress
from app.services.blockchain.ethereum_provider import EthereumProvider
from app.services.deposit_service import DepositService


class EthereumDepositMonitor:
    """Detect ERC-20 deposits and hand them to DepositService."""

    def __init__(
        self,
        provider: EthereumProvider | None = None,
    ) -> None:
        self.provider = provider or EthereumProvider()

    async def process_transaction(
        self,
        db: AsyncSession,
        tx_hash: str,
    ) -> list[Any]:
        """Process ERC-20 transfers contained in one transaction."""

        transfers = (
            await self.provider.get_erc20_transfer_events(tx_hash)
        )

        if not transfers:
            return []

        created_deposits = []

        for transfer in transfers:
            token_address = transfer["token_address"]
            destination = transfer["to"]
            # print("TRANSFER TOKEN:", token_address)
            # print("TRANSFER TO:", destination)

            # ----------------------------------------------------
            # Find the token asset
            # ----------------------------------------------------

            decimals = (
                await self.provider.get_erc20_decimals(
                    token_address
                )
            )

            raw_amount = transfer["amount"]

            amount = Decimal(raw_amount) / (
                Decimal(10) ** decimals
            )

            # ----------------------------------------------------
            # Find BitNova deposit address
            # ----------------------------------------------------

            address_result = await db.execute(
                select(WalletAddress)
                .where(
                    WalletAddress.network
                    == self.provider.network.upper(),
                    func.lower(WalletAddress.address)
                    == destination.lower(),
                    WalletAddress.status == "ACTIVE",
                )
            )

            wallet_address = (
                address_result.scalar_one_or_none()
            )
            # print(
            #     "MATCHED WALLET ADDRESS:",
            #     wallet_address is not None,
            # )

            if wallet_address is None:
                continue

            # ----------------------------------------------------
            # Validate asset
            # ----------------------------------------------------

            asset_result = await db.execute(
                select(Asset)
                .where(
                    Asset.id == wallet_address.asset_id,
                    Asset.is_active.is_(True),
                    Asset.deposit_enabled.is_(True),
                )
            )

            asset = asset_result.scalar_one_or_none()
            # print("MATCHED ASSET:", asset is not None)
            if asset is None:
                continue

            # ----------------------------------------------------
            # Create pending/confirmed deposit
            # ----------------------------------------------------

            confirmations = (
                await self.provider.get_confirmations(
                    tx_hash
                )
            )

            if confirmations is None:
                confirmations = 0

            wallet_result = await db.execute(
                select(Wallet).where(
                    Wallet.id == wallet_address.wallet_id,
                )
    )

            wallet = wallet_result.scalar_one_or_none()

            if wallet is None:
                continue

            deposit = (
                await DepositService.create_pending_deposit(
                    db,
                    user_id=wallet.user_id,
                    wallet_address_id=wallet_address.id,
                    asset_id=asset.id,
                    network=self.provider.network,
                    blockchain_tx_hash=tx_hash,
                    amount=amount,
                    confirmations=confirmations,
                )
            )

            created_deposits.append(deposit)

        return created_deposits

    # @staticmethod
    # def _wallet_user_id(
    #     wallet_address: WalletAddress,
    # ) -> UUID:
    #     """Placeholder until wallet ownership is loaded."""

    #     raise NotImplementedError(
    #         "Wallet ownership lookup must be implemented "
    #         "before processing deposits."
    #     )