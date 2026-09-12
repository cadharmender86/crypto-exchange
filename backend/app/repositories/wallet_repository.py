from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exchange_errors import InsufficientBalanceError
from app.models.wallet import Wallet


class WalletRepository:
    """
    Repository for wallet balance operations.

    All balance mutations used by the exchange engine should happen
    through this repository.
    """

    # --------------------------------------------------
    # Read Wallet
    # --------------------------------------------------
    @staticmethod
    async def get_by_user_asset(
        db: AsyncSession,
        *,
        user_id: UUID,
        asset_id: UUID,
    ) -> Wallet | None:
        result = await db.execute(
            select(Wallet).where(
                Wallet.user_id == user_id,
                Wallet.asset_id == asset_id,
            )
        )
        return result.scalar_one_or_none()

    # --------------------------------------------------
    # Lock Wallet Row (FOR UPDATE)
    # --------------------------------------------------
    @staticmethod
    async def lock_wallet_for_update(
        db: AsyncSession,
        *,
        user_id: UUID,
        asset_id: UUID,
    ) -> Wallet | None:
        result = await db.execute(
            select(Wallet)
            .where(
                Wallet.user_id == user_id,
                Wallet.asset_id == asset_id,
            )
            .with_for_update()
        )
        return result.scalar_one_or_none()

    # --------------------------------------------------
    # Reserve Balance
    # --------------------------------------------------
    @staticmethod
    async def reserve_balance(
        db: AsyncSession,
        *,
        wallet: Wallet,
        amount: Decimal,
    ) -> Wallet:

        if amount <= 0:
            raise ValueError("Reservation amount must be positive.")

        if wallet.balance_available < amount:
            raise InsufficientBalanceError(
                "Insufficient available balance."
            )

        wallet.balance_available -= amount
        wallet.balance_locked += amount

        await db.flush()
        await db.refresh(wallet)

        return wallet

    # --------------------------------------------------
    # Release Reserved Balance
    # --------------------------------------------------
    @staticmethod
    async def release_balance(
        db: AsyncSession,
        *,
        wallet: Wallet,
        amount: Decimal,
    ) -> Wallet:

        if amount <= 0:
            raise ValueError("Release amount must be positive.")

        if wallet.balance_locked < amount:
            raise ValueError(
                "Cannot release more than locked balance."
            )

        wallet.balance_locked -= amount
        wallet.balance_available += amount

        await db.flush()
        await db.refresh(wallet)

        return wallet

    # --------------------------------------------------
    # Consume Locked Balance
    # --------------------------------------------------
    @staticmethod
    async def consume_locked_balance(
        db: AsyncSession,
        *,
        wallet: Wallet,
        amount: Decimal,
    ) -> Wallet:

        if amount <= 0:
            raise ValueError("Consumed amount must be positive.")

        if wallet.balance_locked < amount:
            raise ValueError("Locked balance is insufficient.")

        wallet.balance_locked -= amount

        await db.flush()
        await db.refresh(wallet)

        return wallet