from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WalletBalance(BaseModel):
    account_id: UUID | None = None
    asset_id: UUID
    symbol: str
    name: str
    account_type: str
    available_balance: Decimal
    locked_balance: Decimal

    account_exists: bool
    is_fiat: bool

# class WalletBalanceResponse(BaseModel):
#     model_config = ConfigDict(from_attributes=True)

#     account_id: UUID
#     asset_id: UUID

#     symbol: str
#     name: str

#     account_type: str

#     available_balance: Decimal
#     locked_balance: Decimal

#     is_fiat: bool


class WalletDashboardResponse(BaseModel):
    balances: list[WalletBalance]