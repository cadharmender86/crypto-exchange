from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.account import Account
from app.api.dependencies import get_current_user


router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)


@router.get("")
async def get_my_accounts(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    result = await db.execute(
        select(Account)
        .where(Account.user_id == current_user.id)
    )

    accounts = result.scalars().all()

    return [
        {
            "id": account.id,
            "asset_id": account.asset_id,
            "account_type": account.account_type,
            "available_balance": account.available_balance,
            "locked_balance": account.locked_balance,
            "total_balance": (
                account.available_balance
                + account.locked_balance
            ),
            "status": account.status,
        }
        for account in accounts
    ]