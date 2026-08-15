from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class AdminDepositResponse(BaseModel):
    id: UUID
    user_id: UUID
    user_email: str
    wallet_address_id: UUID
    asset_id: UUID
    network: str
    blockchain_tx_hash: str
    amount: Decimal
    confirmations: int
    status: str
    ledger_transaction_id: UUID | None
    created_at: datetime
    updated_at: datetime


class AdminDepositListResponse(BaseModel):
    items: list[AdminDepositResponse]
    page: int
    page_size: int
    total: int
