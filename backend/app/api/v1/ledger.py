from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db


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
):
    """
    Return ledger entries for an account.

    This endpoint is intentionally read-only.
    Financial transactions must go through the ledger service.
    """

    # Ledger query will be implemented once the
    # ledger_account and ledger_entry models are finalized.

    return {
        "account_id": str(account_id),
        "entries": [],
        "message": "Ledger query endpoint initialized",
    }