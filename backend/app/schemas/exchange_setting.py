from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import SettingValueType


class ExchangeSettingBase(BaseModel):
    key: str = Field(
        min_length=2,
        max_length=100,
    )
    description: str | None = None
    is_public: bool = False


class ExchangeSettingCreate(ExchangeSettingBase):
    value: str
    value_type: str = Field(
        default=SettingValueType.STRING,
    )


class ExchangeSettingUpdate(BaseModel):
    value: str


class ExchangeSettingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key: str
    value: str
    value_type: str
    description: str | None
    is_public: bool
    created_at: datetime
    updated_at: datetime


class ExchangeSettingPublicResponse(BaseModel):
    key: str
    value: str


class ExchangeSettingsMapResponse(BaseModel):
    settings: dict[str, str]


class DefaultMarketResponse(BaseModel):
    default_market: str


class ExchangeFeatureFlagsResponse(BaseModel):
    maintenance_mode: bool
    deposits_enabled: bool
    withdrawals_enabled: bool
    spot_trading_enabled: bool
    margin_trading_enabled: bool
    referral_enabled: bool
    kyc_required_for_withdrawal: bool