from uuid import UUID

from sqlalchemy import select
# from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.wallet import Wallet
from app.models.asset import Asset
from app.services.exchange_setting_service import ExchangeSettingService


class WalletService:

    @staticmethod
    async def create_wallet(
        db: AsyncSession,
        user_id: UUID,
        wallet_type: str = "CUSTOMER",
    ) -> Wallet:

        wallet_type = wallet_type.strip().upper()

        if not wallet_type:
            raise ValueError(
                "Wallet type is required"
            )

        existing = await db.execute(
            select(Wallet).where(
                Wallet.user_id == user_id,
                Wallet.wallet_type == wallet_type,
            )
        )

        wallet = existing.scalar_one_or_none()

        if wallet:
            raise ValueError(
                "Wallet already exists"
            )

        wallet = Wallet(
            user_id=user_id,
            wallet_type=wallet_type,
            status="ACTIVE",
        )

        db.add(wallet)
        # await db.flush()

        try:
            await db.flush()

        except IntegrityError:
            await db.rollback()

            raise ValueError(
                "Wallet already exists"
            )

        await db.refresh(wallet)

        # Automatically allocate Ethereum deposit address
        # asset_result = await db.execute(
        #     select(Asset).where(
        #         Asset.symbol == "USDT"
        #     )
        # )

        # usdt_asset = asset_result.scalar_one()

        # await EthereumWalletService.allocate_deposit_address(
        #     db=db,
        #     wallet_id=wallet.id,
        #     user_id=user_id,
        #     asset_id=usdt_asset.id,
        # )

        return wallet

    @staticmethod
    async def get_wallet(
        db: AsyncSession,
        wallet_id: UUID,
    ) -> Wallet | None:

        result = await db.execute(
            select(Wallet).where(
                Wallet.id == wallet_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_wallet(
        db: AsyncSession,
        user_id: UUID,
        wallet_type: str = "CUSTOMER",
    ) -> Wallet | None:

        wallet_type = wallet_type.strip().upper()

        result = await db.execute(
            select(Wallet).where(
                Wallet.user_id == user_id,
                Wallet.wallet_type == wallet_type,
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def list_user_wallets(
        db: AsyncSession,
        user_id: UUID,
    ) -> list[Wallet]:

        result = await db.execute(
            select(Wallet)
            .where(
                Wallet.user_id == user_id
            )
            .order_by(Wallet.created_at)
        )

        return list(result.scalars().all())

    @staticmethod
    async def get_wallet_dashboard(
        db: AsyncSession,
        *,
        user_id: UUID,
    ):

        deposits_enabled = await ExchangeSettingService.get_boolean(
            db,
            "deposits_enabled",
        )
        # Load all active assets configured on the exchange.
        assets_result = await db.execute(
            select(Asset)
            .where(Asset.is_active.is_(True))
            .order_by(Asset.symbol.asc())
        )

        assets = assets_result.scalars().all()

        # Load all customer accounts for this user.
        accounts_result = await db.execute(
            select(Account)
            .where(
                Account.user_id == user_id,
                Account.account_type == "CUSTOMER",
            )
        )

        accounts = accounts_result.scalars().all()

        # Map accounts by asset_id.
        account_map = {
            account.asset_id: account
            for account in accounts
        }

        balances = []

        for asset in assets:
            account = account_map.get(asset.id)

            balances.append(
                {
                    "account_id": account.id if account else None,
                    "asset_id": asset.id,
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "account_type": "CUSTOMER",
                    "available_balance": (
                        account.available_balance if account else 0
                    ),
                    "locked_balance": (
                        account.locked_balance if account else 0
                    ),
                    "account_exists": account is not None,
                    "is_fiat": asset.asset_type == "FIAT",
                }
            )

        return {

            "exchange": {
                "deposits_enabled": deposits_enabled,
            },
            "balances": balances
        }

    @staticmethod
    async def withdrawals_enabled(
        db: AsyncSession,
    ) -> bool:

        return await ExchangeSettingService.get_boolean(
            db,
            "withdrawals_enabled",
        )