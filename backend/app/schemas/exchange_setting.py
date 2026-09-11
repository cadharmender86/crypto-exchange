from pydantic import BaseModel, Field, ConfigDict

from app.core.constants import SettingValueType


class ExchangeSettingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    key: str
    value: str
    value_type: str
    description: str | None
    is_public: bool


class ExchangeSettingUpdateRequest(BaseModel):
    value: str = Field(..., min_length=1, max_length=5000)


class ExchangeSettingCreateRequest(BaseModel):
    key: str = Field(..., min_length=3, max_length=100)

    value: str = Field(..., min_length=1, max_length=5000)

    value_type: str = Field(
        default=SettingValueType.STRING,
    )

    description: str | None = None

    is_public: bool = False