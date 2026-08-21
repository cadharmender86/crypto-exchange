from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.withdrawal import WithdrawalStatus


class AdminWithdrawalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    user_email: str

    account_id: UUID
    asset_id: UUID

    network: str
    destination_address: str

    amount: Decimal

    status: WithdrawalStatus

    confirmations: int = 0

    blockchain_tx_hash: str | None = None
    failure_reason: str | None = None

    ledger_transaction_id: UUID | None = None

    broadcasted_at: datetime | None = None
    completed_at: datetime | None = None

    created_at: datetime
    updated_at: datetime


class AdminWithdrawalListResponse(BaseModel):
    items: list[AdminWithdrawalResponse]
    page: int
    page_size: int
    total: int


class WithdrawalReviewRequest(BaseModel):
    reason: str | None = Field(
        default=None,
        max_length=255,
    )