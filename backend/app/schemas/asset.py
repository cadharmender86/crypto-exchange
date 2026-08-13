from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    symbol: str
    name: str
    asset_type: str
    decimal_places: int
    is_active: bool
    deposit_enabled: bool
    withdrawal_enabled: bool
    trading_enabled: bool