from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.account import Account
from app.models.asset import Asset
from app.models.ledger_entry import LedgerEntry
from app.models.ledger_transaction import LedgerTransaction
from app.models.user import User


router = APIRouter(
    prefix="/ledger",
    tags=["Ledger"],
)

transactions_router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.get("/accounts/{account_id}/entries")
async def get_ledger_entries(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return ledger entries for an account owned by the current user."""
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this account",
        )

    return {
        "account_id": str(account.id),
        "entries": [],
        "message": "Ledger query endpoint initialized",
    }


@transactions_router.get("/history")
async def get_transaction_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return recent ledger activity for the authenticated user."""
    result = await db.execute(
        select(LedgerTransaction, LedgerEntry, Asset)
        .join(LedgerEntry, LedgerEntry.transaction_id == LedgerTransaction.id)
        .join(Account, Account.id == LedgerEntry.account_id)
        .join(Asset, Asset.id == Account.asset_id)
        .where(Account.user_id == current_user.id)
        .order_by(desc(LedgerTransaction.created_at))
        .limit(limit)
    )

    rows = result.all()

    return [
        {
            "id": str(transaction.id),
            "reference": transaction.reference,
            "type": transaction.transaction_type,
            "status": transaction.status,
            "description": transaction.description,
            "asset": asset.symbol,
            "amount": str(entry.amount),
            "entry_type": entry.entry_type,
            "direction": "CREDIT" if entry.entry_type.upper() == "CREDIT" else "DEBIT",
            "created_at": transaction.created_at.isoformat(),
        }
        for transaction, entry, asset in rows
    ]
