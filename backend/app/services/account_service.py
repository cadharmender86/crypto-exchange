from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.asset import Asset


class AccountService:

    @staticmethod
    async def get_or_create_account(
        db: AsyncSession,
        user_id: UUID,
        asset_id: UUID,
        lock: bool = False,
    ) -> Account | None:

        query = await db.execute(
            select(Account)
            .where(
                Account.user_id == user_id,
                Account.asset_id == asset_id,
                Account.account_type == "CUSTOMER",
            )
        )

        if lock:
            query = query.with_for_update()

        result = await db.execute(query)   


        return result.scalar_one_or_none()