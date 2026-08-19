from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateOrderRequest(BaseModel):
    base_asset_id: UUID
    quote_asset_id: UUID
    side: str = Field(pattern="^(BUY|SELL)$")
    order_type: str = Field(default="LIMIT", pattern="^LIMIT$")
    price: Decimal = Field(gt=0, max_digits=38, decimal_places=18)
    quantity: Decimal = Field(gt=0, max_digits=38, decimal_places=18)
    client_order_id: str | None = Field(default=None, min_length=1, max_length=100)


class OrderResponse(BaseModel):
    id: UUID
    base_asset_id: UUID
    quote_asset_id: UUID
    symbol: str | None = None
    amount: Decimal | None = None
    client_order_id: str | None
    side: str
    order_type: str
    status: str
    price: Decimal | None
    quantity: Decimal
    filled_quantity: Decimal
    remaining_quantity: Decimal
    average_execution_price: Decimal | None
    fee_amount: Decimal
    fee_asset_id: UUID | None
    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None

    model_config = {"from_attributes": True}
