from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.core.exchange_errors import InsufficientBalanceError


class AccountRepository:

    @staticmethod
    async def get_by_user_asset(
        db: AsyncSession,
        *,
        user_id: UUID,
        asset_id: UUID,
    ) -> Account | None:
        result = await db.execute(
            select(Account).where(
                Account.user_id == user_id,
                Account.asset_id == asset_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def lock_account_for_update(
        db: AsyncSession,
        *,
        user_id: UUID,
        asset_id: UUID,
    ) -> Account | None:
        result = await db.execute(
            select(Account)
            .where(
                Account.user_id == user_id,
                Account.asset_id == asset_id,
            )
            .with_for_update()
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def reserve_balance(
        db: AsyncSession,
        *,
        account: Account,
        amount: Decimal,
    ) -> Account:

        if amount <= 0:
            raise ValueError("Reservation amount must be positive.")

        if account.available_balance < amount:
            raise InsufficientBalanceError("Insufficient available balance.")

        account.available_balance -= amount
        account.locked_balance += amount

        await db.flush()
        await db.refresh(account)

        return account

    @staticmethod
    async def release_balance(
        db: AsyncSession,
        *,
        account: Account,
        amount: Decimal,
    ) -> Account:

        if amount <= 0:
            raise ValueError("Release amount must be positive.")

        if account.locked_balance < amount:
            raise ValueError("Cannot release more than locked balance.")

        account.locked_balance -= amount
        account.available_balance += amount

        await db.flush()
        await db.refresh(account)

        return account

    @staticmethod
    async def consume_locked_balance(
        db: AsyncSession,
        *,
        account: Account,
        amount: Decimal,
    ) -> Account:

        if amount <= 0:
            raise ValueError("Consumed amount must be positive.")

        if account.locked_balance < amount:
            raise ValueError("Locked balance is insufficient.")

        account.locked_balance -= amount

        await db.flush()
        await db.refresh(account)

        return account