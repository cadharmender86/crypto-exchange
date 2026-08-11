from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class LedgerEntryResponse(BaseModel):
    id: UUID
    account_id: UUID
    entry_type: str
    amount: Decimal


class LedgerTransactionResponse(BaseModel):
    id: UUID
    reference: str
    transaction_type: str
    status: str
    description: str | None