from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class AdminWithdrawalResponse(BaseModel):
    id: UUID
    user_id: UUID
    user_email: str
    account_id: UUID
    asset_id: UUID
    network: str
    destination_address: str
    amount: Decimal
    status: str
    idempotency_key: str
    ledger_transaction_id: UUID | None
    created_at: datetime
    updated_at: datetime


class AdminWithdrawalListResponse(BaseModel):
    items: list[AdminWithdrawalResponse]
    page: int
    page_size: int
    total: int


class WithdrawalReviewRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)
