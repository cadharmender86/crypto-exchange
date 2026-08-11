from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class AccountResponse(BaseModel):
    id: UUID
    asset_id: UUID
    account_type: str
    available_balance: Decimal
    locked_balance: Decimal
    total_balance: Decimal
    status: str