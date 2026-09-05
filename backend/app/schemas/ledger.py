from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LedgerEntryResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    entry_type: str
    amount: Decimal

    


class LedgerTransactionResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reference: str
    transaction_type: str
    status: str
    description: str | None
    created_at: datetime

    ledger_entries: list[LedgerEntryResponse] = []

    