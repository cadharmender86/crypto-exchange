from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.asset import Asset


class AccountService:
    CUSTOMER_ACCOUNT_TYPE = "CUSTOMER"

    @staticmethod
    async def get_or_create_account(
        db: AsyncSession,
        user_id: UUID,
        asset_id: UUID,
        lock: bool = False,
    ) -> Account | None:
        query = select(Account).where(
            Account.user_id == user_id,
            Account.asset_id == asset_id,
            Account.account_type == AccountService.CUSTOMER_ACCOUNT_TYPE,
        )

        if lock:
            query = query.with_for_update()

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_customer_accounts(
        db: AsyncSession,
        user_id: UUID,
    ) -> list[Account]:
        result = await db.execute(
            select(Asset).where(Asset.is_active.is_(True))
        )
        assets = result.scalars().all()

        accounts: list[Account] = []

        for asset in assets:
            existing = await db.execute(
                select(Account).where(
                    Account.user_id == user_id,
                    Account.asset_id == asset.id,
                    Account.account_type
                    == AccountService.CUSTOMER_ACCOUNT_TYPE,
                )
            )

            if existing.scalar_one_or_none() is not None:
                continue

            account = Account(
                user_id=user_id,
                asset_id=asset.id,
                account_type=AccountService.CUSTOMER_ACCOUNT_TYPE,
                available_balance=Decimal("0"),
                locked_balance=Decimal("0"),
                status="ACTIVE",
            )

            db.add(account)
            accounts.append(account)

        await db.flush()
        return accounts