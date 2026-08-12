from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.account import Account
from app.models.user import User


router = APIRouter(
    prefix="/ledger",
    tags=["Ledger"],
)


@router.get(
    "/accounts/{account_id}/entries",
)
async def get_ledger_entries(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return ledger entries for an account.

    A user may only access ledger data belonging
    to their own account.
    """

    # ---------------------------------------------------------
    # 1. Find the requested account
    # ---------------------------------------------------------
    result = await db.execute(
        select(Account).where(
            Account.id == account_id
        )
    )

    account = result.scalar_one_or_none()

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    # ---------------------------------------------------------
    # 2. Authorization / ownership check
    # ---------------------------------------------------------
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account",
        )

    # ---------------------------------------------------------
    # 3. Ledger query
    #
    # The actual ledger-entry retrieval will be implemented
    # separately. For now we preserve the existing response.
    # ---------------------------------------------------------
    return {
        "account_id": str(account.id),
        "entries": [],
        "message": "Ledger query endpoint initialized",
    }