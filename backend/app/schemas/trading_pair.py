from decimal import Decimal
from pydantic import BaseModel
from uuid import UUID


class TradingPairCreate(BaseModel):
    base_asset_id: UUID
    quote_asset_id: UUID
    pair_code: str
    display_name: str
    tick_size: Decimal
    step_size: Decimal
    minimum_order_quantity: Decimal
    minimum_order_value: Decimal


class TradingPairUpdate(BaseModel):
    status: str | None = None
    is_visible: bool | None = None
    is_default: bool | None = None
    price_precision: int | None = None
    quantity_precision: int | None = None


class TradingPairResponse(BaseModel):
    id: UUID
    pair_code: str
    display_name: str
    status: str
    is_visible: bool
    is_default: bool

    class Config:
        from_attributes = True