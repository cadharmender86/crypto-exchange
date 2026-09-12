from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


# =====================================================
# Exchange Settings
# =====================================================

class ExchangeSettingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str
    value_type: str
    description: str | None
    is_public: bool


class UpdateExchangeSettingRequest(BaseModel):
    value: str = Field(..., min_length=1)


# =====================================================
# Trading Pair Responses
# =====================================================

class TradingPairResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str

    pair_code: str
    display_name: str

    base_asset: str
    quote_asset: str

    price_precision: int
    quantity_precision: int

    tick_size: Decimal
    step_size: Decimal

    min_order_quantity: Decimal
    max_order_quantity: Decimal | None
    min_order_value: Decimal

    status: str
    is_visible: bool
    is_default: bool


# =====================================================
# Create Trading Pair
# =====================================================

class CreateTradingPairRequest(BaseModel):
    base_symbol: str = Field(..., max_length=20)
    quote_symbol: str = Field(..., max_length=20)

    display_name: str = Field(..., max_length=30)

    price_precision: int = Field(..., ge=0, le=18)
    quantity_precision: int = Field(..., ge=0, le=18)

    tick_size: Decimal
    step_size: Decimal

    min_order_quantity: Decimal
    max_order_quantity: Decimal | None = None
    min_order_value: Decimal


# =====================================================
# Update Pair Status
# =====================================================

class UpdateTradingPairStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(ACTIVE|SUSPENDED|DISABLED)$")