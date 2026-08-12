from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WalletCreateRequest(BaseModel):
    wallet_type: str = "CUSTOMER"


class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    wallet_type: str
    status: str
    created_at: datetime
    updated_at: datetime