from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AdminOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    user_email: str
    base_asset: str
    quote_asset: str
    client_order_id: str | None = None
    side: str
    order_type: str
    status: str
    price: Decimal | None = None
    quantity: Decimal
    filled_quantity: Decimal
    remaining_quantity: Decimal
    average_execution_price: Decimal | None = None
    fee_amount: Decimal
    fee_asset: str | None = None
    created_at: datetime
    updated_at: datetime
    cancelled_at: datetime | None = None


class AdminOrderListResponse(BaseModel):
    items: list[AdminOrderResponse]
    page: int
    page_size: int
    total: int
