from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TransferRequest(BaseModel):

    to_user_id: UUID

    asset_id: UUID

    amount: Decimal = Field(
        gt=0,
        max_digits=38,
        decimal_places=18,
    )

    description: str | None = None


class TransferResponse(BaseModel):

    transaction_id: UUID
    reference: str
    status: str