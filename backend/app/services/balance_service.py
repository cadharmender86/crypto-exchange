from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class BalanceService:

    @staticmethod
    async def get_locked_account(
        db: AsyncSession,
        account_id: UUID,
    ) -> Account:

        result = await db.execute(
            select(Account)
            .where(Account.id == account_id)
            .with_for_update()
        )

        account = result.scalar_one_or_none()

        if account is None:
            raise ValueError("Account not found")

        return account

    @staticmethod
    async def debit(
        account: Account,
        amount: Decimal,
    ) -> None:

        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError(
                "Amount must be greater than zero"
            )

        if account.available_balance < amount:
            raise ValueError(
                "Insufficient available balance"
            )

        account.available_balance -= amount

    @staticmethod
    async def credit(
        account: Account,
        amount: Decimal,
    ) -> None:

        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError(
                "Amount must be greater than zero"
            )

        account.available_balance += amount

    @staticmethod
    async def lock(
        account: Account,
        amount: Decimal,
    ) -> None:

        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError(
                "Amount must be greater than zero"
            )

        if account.available_balance < amount:
            raise ValueError(
                "Insufficient available balance"
            )

        account.available_balance -= amount
        account.locked_balance += amount

    @staticmethod
    async def unlock(
        account: Account,
        amount: Decimal,
    ) -> None:

        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError(
                "Amount must be greater than zero"
            )

        if account.locked_balance < amount:
            raise ValueError(
                "Insufficient locked balance"
            )

        account.locked_balance -= amount
        account.available_balance += amount