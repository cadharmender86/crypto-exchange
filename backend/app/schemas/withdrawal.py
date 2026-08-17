from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WithdrawalCreate(BaseModel):
    account_id: UUID
    asset_id: UUID
    network: str = Field(min_length=1, max_length=30)
    destination_address: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(
        gt=0,
        max_digits=38,
        decimal_places=18,
    )


class WithdrawalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    account_id: UUID
    asset_id: UUID
    network: str
    destination_address: str
    amount: Decimal
    status: str
    idempotency_key: str
    ledger_transaction_id: UUID | None
    created_at: object
    updated_at: object
