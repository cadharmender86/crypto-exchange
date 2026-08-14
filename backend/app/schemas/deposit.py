from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DepositCreate(BaseModel):
    wallet_address_id: UUID
    asset_id: UUID
    network: str = Field(min_length=1, max_length=30)
    blockchain_tx_hash: str = Field(
        min_length=1,
        max_length=255,
    )
    amount: Decimal = Field(
        gt=0,
        max_digits=38,
        decimal_places=18,
    )


class DepositResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    wallet_address_id: UUID
    asset_id: UUID
    network: str
    blockchain_tx_hash: str
    amount: Decimal
    confirmations: int
    status: str
    ledger_transaction_id: UUID | None
    