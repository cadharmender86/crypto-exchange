from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class TradeHistoryResponse(BaseModel):
    id: UUID
    symbol: str
    side: str
    price: Decimal
    amount: Decimal
    total: Decimal
    fee: Decimal
    created_at: datetime
