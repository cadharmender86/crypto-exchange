from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.admin_auth import require_permission
from app.core.database import get_db
from app.models.admin import AdminUser, AuditLog
from app.models.user import User
from app.models.deposit import Deposit
from app.models.account import Account
from app.models.bank_account import BankAccount
from app.models.fiat_deposit import FiatDeposit
from app.models.withdrawal import Withdrawal
from app.models.kyc import KYCRecord
from app.schemas.admin import (
    UserListResponse,
    UserListItemResponse,
    UserDetailResponse,
    UserBalanceResponse,
    UserBankAccountResponse,
    UserKYCResponse,
    TransactionSummaryResponse,
    UserDepositResponse,
    UserWithdrawalResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["Admin Users"],
)


@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(require_permission("USER_READ")),
):
    query = select(User)

    if search:
        query = query.where(User.email.ilike(f"%{search}%"))

    total = await db.scalar(
        select(func.count()).select_from(query.subquery())
    ) or 0

    result = await db.scalars(
        query.order_by(User.created_at.desc())
        .limit(page_size)
        .offset((page - 1) * page_size)
    )

    users = result.all()

    return UserListResponse(
        items=[UserListItemResponse.model_validate(user) for user in users],
        page=page,
        page_size=page_size,
        total=total,
    )

@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
)
async def get_user_detail(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(require_permission("USER_READ")),
):
    query = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.accounts).selectinload(Account.asset),
            selectinload(User.bank_accounts),
        )
    )

    result = await db.scalar(query)

    if result is None:
        raise HTTPException(status_code=404, detail="User not found.")

    kyc_record = await db.scalar(
        select(KYCRecord).where(KYCRecord.user_id == user_id)
    )

    fiat_deposits = list(
        await db.scalars(
            select(FiatDeposit)
            .where(FiatDeposit.user_id == user_id)
            .order_by(FiatDeposit.created_at.desc())
            .limit(10)
        )
    )

    crypto_deposits = list(
        await db.scalars(
            select(Deposit)
            .where(Deposit.user_id == user_id)
            .order_by(Deposit.created_at.desc())
            .limit(10)
        )
    )

    crypto_withdrawals = list(
        await db.scalars(
            select(Withdrawal)
            .where(Withdrawal.user_id == user_id)
            .order_by(Withdrawal.created_at.desc())
            .limit(10)
        )
    )

    fiat_deposit_count = (
        await db.scalar(
            select(func.count())
            .select_from(FiatDeposit)
            .where(FiatDeposit.user_id == user_id)
        )
    ) or 0

    crypto_deposit_count = (
        await db.scalar(
            select(func.count())
            .select_from(Deposit)
            .where(Deposit.user_id == user_id)
        )
    ) or 0

    deposit_count = fiat_deposit_count + crypto_deposit_count

    withdrawal_count = (
        await db.scalar(
            select(func.count())
            .select_from(Withdrawal)
            .where(Withdrawal.user_id == user_id)
        )
    ) or 0

    balances = [
        UserBalanceResponse(
            asset_symbol=account.asset.symbol,
            available_balance=account.available_balance,
            locked_balance=account.locked_balance,
        )
        for account in result.accounts
    ]

    bank_accounts = [
        UserBankAccountResponse(
            id=bank.id,
            bank_name=bank.bank_name,
            account_holder_name=bank.account_holder_name,
            account_number=bank.account_number,
            ifsc_code=bank.ifsc_code,
            account_type=bank.account_type.value,
            status=bank.status.value,
            is_primary=bank.is_primary,
            verified_at=bank.verified_at,
        )
        for bank in result.bank_accounts
    ]

    kyc = None
    if kyc_record:
        kyc = UserKYCResponse(
            status=(
                kyc_record.status.value
                if hasattr(kyc_record.status, "value")
                else str(kyc_record.status)
            ),
            full_name=kyc_record.full_name,
            pan_number=kyc_record.pan_number,
            aadhaar_number=kyc_record.aadhaar_number,
            reviewed_at=kyc_record.reviewed_at,
        )
    recent_deposits_response = []

    #INR Deposits
    for d in fiat_deposits:
        recent_deposits_response.append(
            UserDepositResponse(
                id=d.id,
                amount=d.amount,
                asset_symbol="INR",
                network=
                    d.provider_metadata.get("payment_method", "BANK TRANSFER")
                    if d.provider_metadata
                    else "BANK_TRANSFER",                                                           #UPI / IMPS / NEFT
                status=d.status.value if hasattr(d.status, "value") else str(d.status),
                created_at=d.created_at,
                blockchain_tx_hash=None,
                confirmations=None,
                transaction_reference=d.utr_number,
                deposit_type="FIAT",
            )
        )

    #Crypto Deposits    
    for d in crypto_deposits:
        recent_deposits_response.append(
            UserDepositResponse(
            id=d.id,
            amount=d.amount,
            asset_symbol=d.asset.symbol,
            network=d.network,
            status=d.status.value if hasattr(d.status, "value") else str(d.status),
            created_at=d.created_at,
            blockchain_tx_hash=d.blockchain_tx_hash,
            confirmations=d.confirmations,
            deposit_type="CRYPTO",
        )
    )

    recent_deposits_response.sort(
        key=lambda x: x.created_at,
        reverse=True,
    )

    recent_deposits_response = recent_deposits_response[:10]    
    
    transaction_summary = TransactionSummaryResponse(
        deposits=deposit_count,
        withdrawals=withdrawal_count,
    )

    recent_withdrawals_response = [
        UserWithdrawalResponse(
            id=w.id,
            withdrawal_type="CRYPTO",
            asset_symbol=w.asset.symbol,
            network=w.network,
            amount=w.amount,
            status=w.status.value if hasattr(w.status, "value") else str(w.status),
            destination_address=w.destination_address,
            created_at=w.created_at,
        )
        for w in crypto_withdrawals
    ]   

    return UserDetailResponse(
        id=result.id,
        email=result.email,
        is_active=result.is_active,
        is_verified=result.is_verified,
        two_factor_enabled=result.two_factor_enabled,

        last_login_at=result.last_login_at,
        created_at=result.created_at,
        updated_at=result.updated_at,

        balances=balances,
        bank_accounts=bank_accounts,
        kyc=kyc,

        transaction_summary = transaction_summary,

        recent_deposits= recent_deposits_response,

        recent_withdrawals= recent_withdrawals_response,   
    )        

class UserActionResponse(BaseModel):
    message: str


@router.post(
    "/{user_id}/freeze",
    response_model=UserActionResponse,
)
async def freeze_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_permission("USER_SUSPEND")),
):
    user = await db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_active = False

    audit = AuditLog(
        admin_user_id=admin.id,
        action="USER_SUSPENDED",
        resource_type="USER",
        resource_id=str(user.id),
        result="SUCCESS",
        reason="User suspended from admin panel",
    )

    db.add(audit)

    await db.commit()
    await db.refresh(user)

    return UserActionResponse(
        message="User account frozen successfully."
    )

@router.post(
    "/{user_id}/unfreeze",
    response_model=UserActionResponse,
)
async def unfreeze_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_permission("USER_ACTIVATE")),
):
    user = await db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_active = True

    audit = AuditLog(
        admin_user_id=admin.id,
        action="USER_ACTIVATED",
        resource_type="USER",
        resource_id=str(user.id),
        result="SUCCESS",
        reason="User activated from admin panel",
    )

    db.add(audit)

    await db.commit()
    await db.refresh(user)

    return UserActionResponse(
        message="User account activated successfully."
    )