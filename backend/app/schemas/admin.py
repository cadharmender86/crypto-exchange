from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AdminUserDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AdminUserListResponse(BaseModel):
    items: list[AdminUserDetailResponse]
    page: int
    page_size: int
    total: int


class AdminUserActionRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class AdminDashboardResponse(BaseModel):
    total_users: int
    active_users: int
    verified_users: int
    pending_kyc: int
    total_deposits: int
    total_withdrawals: int
    pending_withdrawals: int
    active_assets: int

class FiatDepositListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_name: str
    user_email: str
    bank_name: str
    utr_number: str
    amount: Decimal
    currency: str
    status: str
    created_at: datetime

class FiatDepositListResponse(BaseModel):
    items: list[FiatDepositListItem]
    total: int

class FiatDepositDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    user_name: str
    user_email: str

    bank_name: str
    account_holder_name: str
    account_number: str
    ifsc_code: str

    utr_number: str
    amount: Decimal
    currency: str
    status: str

    remarks: str | None = None
    rejection_reason: str | None = None

    approved_at: datetime | None = None
    created_at: datetime    

class ApproveDepositRequest(BaseModel):
    remarks: str | None = None


class RejectDepositRequest(BaseModel):
    rejection_reason: str

class ApproveDepositResponse(BaseModel):
    success: bool
    message: str
    deposit_id: UUID
    status: str

class RejectDepositResponse(BaseModel):
    success: bool
    message: str
    deposit_id: UUID
    status: str
            
class UserListItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool
    last_login_at: datetime | None = None
    created_at: datetime


class UserListResponse(BaseModel):
    items: list[UserListItemResponse]
    page: int
    page_size: int
    total: int
    
class AdminAuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    admin_user_id: UUID | None
    action: str
    resource_type: str
    resource_id: str | None
    old_value: dict | None
    new_value: dict | None
    ip_address: str | None
    user_agent: str | None
    result: str
    reason: str | None
    created_at: datetime

# ---------------------------------------------------
# Customer User Detail
# ---------------------------------------------------

class UserBalanceResponse(BaseModel):
    asset_symbol: str
    available_balance: Decimal
    locked_balance: Decimal


class UserBankAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_holder_name: str
    bank_name: str
    account_number: str
    ifsc_code: str

    account_type: str
    status: str
    is_primary: bool
    verified_at: datetime | None = None


class UserKYCResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str | None = None
    full_name: str | None = None
    pan_number: str | None = None
    aadhaar_number: str | None = None
    reviewed_at: datetime | None = None

# -----------------------------
# Transaction Summary
# -----------------------------
class TransactionSummaryResponse(BaseModel):
    deposits: int
    withdrawals: int


# -----------------------------
# Deposit Response
# -----------------------------
class UserDepositResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    deposit_type: str              # INR / CRYPTO

    asset_symbol: str              # INR / USDT / BTC / SOL
    network: str | None = None     # UPI / TRC20 / ERC20 / SOLANA

    amount: Decimal
    status: str

    blockchain_tx_hash: str | None = None
    confirmations: int | None = None

    transaction_reference: str | None = None

    created_at: datetime


# -----------------------------
# Withdrawal Response
# -----------------------------
class UserWithdrawalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    withdrawal_type: str           # FIAT / CRYPTO

    asset_symbol: str
    network: str | None = None

    amount: Decimal
    status: str

    destination_address: str | None = None

    created_at: datetime

class UserDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    is_active: bool
    is_verified: bool
    two_factor_enabled: bool

    last_login_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    balances: list[UserBalanceResponse]

    bank_accounts: list[UserBankAccountResponse]

    kyc: UserKYCResponse | None = None

    transaction_summary: TransactionSummaryResponse

    recent_deposits: list[UserDepositResponse]

    recent_withdrawals: list[UserWithdrawalResponse]