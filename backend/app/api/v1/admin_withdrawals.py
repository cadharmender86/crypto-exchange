from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.services.audit_service import AuditService
from app.api.v1.admin_auth import require_permission
from app.models.admin import AdminUser
from app.models.user import User
from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.services.withdrawal_service import WithdrawalService
from app.schemas.admin_withdrawal import (
    AdminWithdrawalListResponse,
    AdminWithdrawalResponse,
    WithdrawalReviewRequest,
)



router = APIRouter(prefix="/admin/withdrawals", tags=["Admin Withdrawals"])


def _response(withdrawal: Withdrawal, email: str) -> AdminWithdrawalResponse:
    return AdminWithdrawalResponse(
        id=withdrawal.id,
        user_id=withdrawal.user_id,
        user_email=email,

        account_id=withdrawal.account_id,
        asset_id=withdrawal.asset_id,

        network=withdrawal.network,
        destination_address=withdrawal.destination_address,

        amount=withdrawal.amount,

        status=WithdrawalStatus(withdrawal.status),

        confirmations=withdrawal.confirmations,

        blockchain_tx_hash=withdrawal.blockchain_tx_hash,
        failure_reason=withdrawal.failure_reason,
       
        ledger_transaction_id=withdrawal.ledger_transaction_id,

        broadcasted_at=withdrawal.broadcasted_at,
        completed_at=withdrawal.completed_at,

        created_at=withdrawal.created_at,
        updated_at=withdrawal.updated_at,
    )


@router.get("", response_model=AdminWithdrawalListResponse)
async def list_withdrawals(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status", min_length=1, max_length=20),
    search: str | None = Query(None, min_length=1, max_length=255),
    _: AdminUser = Depends(require_permission("WITHDRAWAL_READ")),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if status_filter:
        try:
            status_value = WithdrawalStatus(
                status_filter.strip().upper()
            ).value
            filters.append(Withdrawal.status == status_value)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid withdrawal status",
            )    
    if search:
        term = f"%{search.strip().lower()}%"
        filters.append(
            (func.lower(User.email).like(term))
            | (func.lower(Withdrawal.destination_address).like(term))
        )

    base = select(Withdrawal, User.email).join(User, User.id == Withdrawal.user_id)
    total = (
        await db.execute(
            select(func.count(Withdrawal.id))
            .select_from(Withdrawal)
            .join(User, User.id == Withdrawal.user_id)
            .where(*filters)
        )
    ).scalar_one()

    rows = (
        await db.execute(
            base.where(*filters)
            .order_by(Withdrawal.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).all()

    return AdminWithdrawalListResponse(
        items=[_response(withdrawal, email) for withdrawal, email in rows],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{withdrawal_id}", response_model=AdminWithdrawalResponse)
async def get_withdrawal(
    withdrawal_id: UUID,
    _: AdminUser = Depends(require_permission("WITHDRAWAL_READ")),
    db: AsyncSession = Depends(get_db),
):
    row = (
        await db.execute(
            select(Withdrawal, User.email)
            .join(User, User.id == Withdrawal.user_id)
            .where(Withdrawal.id == withdrawal_id)
        )
    ).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    withdrawal, email = row
    return _response(withdrawal, email)


async def _review(
    withdrawal_id: UUID,
    request: Request,
    payload: WithdrawalReviewRequest,
    admin: AdminUser,
    db: AsyncSession,
    target_status: str,
) -> AdminWithdrawalResponse:
    row = (
        await db.execute(
            select(Withdrawal, User.email)
            .join(User, User.id == Withdrawal.user_id)
            .where(Withdrawal.id == withdrawal_id)
            .with_for_update()
        )
    ).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Withdrawal not found")

    withdrawal, email = row
    if withdrawal.status != WithdrawalStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Withdrawal is already {withdrawal.status.lower()}",
        )

    old_status = withdrawal.status
    try:
        if target_status == WithdrawalStatus.APPROVED.value:
            await WithdrawalService.approve_by_admin(
                db=db,
                withdrawal=withdrawal,
            )
        elif target_status == WithdrawalStatus.REJECTED.value:    
            await WithdrawalService.reject_by_admin(
                db=db,
                withdrawal=withdrawal,
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        )

    await AuditService.log_action(
        db=db,
        admin=admin,
        action=f"WITHDRAWAL_{target_status}",
        resource_type="WITHDRAWAL",
        resource_id=withdrawal.id,
        old_value={"status": old_status},
        new_value={"status": target_status},
        reason=payload.reason,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )  
    
    await db.commit()
    await db.refresh(withdrawal)
    return _response(withdrawal, email)


@router.post("/{withdrawal_id}/approve", response_model=AdminWithdrawalResponse)
async def approve_withdrawal(
    withdrawal_id: UUID,
    request: Request,
    payload: WithdrawalReviewRequest,
    admin: AdminUser = Depends(require_permission("WITHDRAWAL_APPROVE")),
    db: AsyncSession = Depends(get_db),
):
    return await _review(withdrawal_id, request, payload, admin, db, WithdrawalStatus.APPROVED.value)


@router.post("/{withdrawal_id}/reject", response_model=AdminWithdrawalResponse)
async def reject_withdrawal(
    withdrawal_id: UUID,
    request: Request,
    payload: WithdrawalReviewRequest,
    admin: AdminUser = Depends(require_permission("WITHDRAWAL_REJECT")),
    db: AsyncSession = Depends(get_db),
):
    return await _review(withdrawal_id, request, payload, admin, db, WithdrawalStatus.REJECTED.value)
