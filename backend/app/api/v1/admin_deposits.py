from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.api.v1.admin_auth import require_permission
from app.models.admin import AdminUser
from app.models.deposit import Deposit
from app.models.user import User
from app.schemas.admin_deposit import AdminDepositListResponse, AdminDepositResponse


router = APIRouter(prefix="/admin/deposits", tags=["Admin Deposits"])


def _response(deposit: Deposit, email: str) -> AdminDepositResponse:
    return AdminDepositResponse(
        id=deposit.id,
        user_id=deposit.user_id,
        user_email=email,
        wallet_address_id=deposit.wallet_address_id,
        asset_id=deposit.asset_id,
        network=deposit.network,
        blockchain_tx_hash=deposit.blockchain_tx_hash,
        amount=deposit.amount,
        confirmations=deposit.confirmations,
        status=deposit.status,
        ledger_transaction_id=deposit.ledger_transaction_id,
        created_at=deposit.created_at,
        updated_at=deposit.updated_at,
    )


@router.get("", response_model=AdminDepositListResponse)
async def list_deposits(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status", min_length=1, max_length=20),
    search: str | None = Query(None, min_length=1, max_length=255),
    _: AdminUser = Depends(require_permission("DEPOSIT_READ")),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if status_filter:
        filters.append(Deposit.status == status_filter.strip().upper())
    if search:
        term = f"%{search.strip().lower()}%"
        filters.append(
            (func.lower(User.email).like(term))
            | (func.lower(Deposit.blockchain_tx_hash).like(term))
        )

    base = select(Deposit, User.email).join(User, User.id == Deposit.user_id)
    count_result = await db.execute(
        select(func.count(Deposit.id))
        .select_from(Deposit)
        .join(User, User.id == Deposit.user_id)
        .where(*filters)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        base.where(*filters)
        .order_by(Deposit.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    rows = result.all()
    return AdminDepositListResponse(
        items=[_response(deposit, email) for deposit, email in rows],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{deposit_id}", response_model=AdminDepositResponse)
async def get_deposit(
    deposit_id: UUID,
    _: AdminUser = Depends(require_permission("DEPOSIT_READ")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Deposit, User.email)
        .join(User, User.id == Deposit.user_id)
        .where(Deposit.id == deposit_id)
    )
    row = result.one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found",
        )

    deposit, email = row
    return _response(deposit, email)
