from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TradingPairResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    pair_code: str
    display_name: str

    base_asset_id: UUID
    quote_asset_id: UUID

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

    created_at: str
    updated_at: str


class TradingPairCreateRequest(BaseModel):
    base_asset_symbol: str = Field(..., min_length=2, max_length=20)
    quote_asset_symbol: str = Field(..., min_length=2, max_length=20)

    display_name: str = Field(..., min_length=3, max_length=30)

    price_precision: int = Field(default=2, ge=0, le=12)
    quantity_precision: int = Field(default=8, ge=0, le=18)

    tick_size: Decimal = Field(..., gt=0)
    step_size: Decimal = Field(..., gt=0)

    min_order_quantity: Decimal = Field(..., gt=0)
    max_order_quantity: Decimal | None = Field(default=None, gt=0)

    min_order_value: Decimal = Field(..., gt=0)

    is_visible: bool = True
    is_default: bool = False

    @field_validator(
        "base_asset_symbol",
        "quote_asset_symbol",
        mode="before",
    )
    @classmethod
    def normalize_symbols(cls, value: str):
        return value.strip().upper()


class TradingPairUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=3, max_length=30)

    price_precision: int | None = Field(default=None, ge=0, le=12)
    quantity_precision: int | None = Field(default=None, ge=0, le=18)

    tick_size: Decimal | None = Field(default=None, gt=0)
    step_size: Decimal | None = Field(default=None, gt=0)

    min_order_quantity: Decimal | None = Field(default=None, gt=0)
    max_order_quantity: Decimal | None = Field(default=None, gt=0)

    min_order_value: Decimal | None = Field(default=None, gt=0)

    status: str | None = None

    is_visible: bool | None = None
    is_default: bool | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None):
        if value is None:
            return value

        value = value.upper()

        allowed = {
            "ACTIVE",
            "DISABLED",
            "SUSPENDED",
        }

        if value not in allowed:
            raise ValueError("Invalid trading pair status.")

        return value