from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class CreatePaymentOrderRequest(BaseModel):
    amount: Decimal = Field(gt=99, le=200000)

    currency: str = "INR"


class PaymentOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gateway_order_id: str

    payment_session_id: str

    gateway_order_id: str

    amount: Decimal

    currency: str

    expires_at: datetime

class PaymentHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    gateway_order_id: str
    gateway_payment_id: str | None

    amount: Decimal
    currency: str

    status: str

    created_at: datetime
    completed_at: datetime | None

class PaymentHistoryResponse(BaseModel):
    items: list[PaymentHistoryItem]

class PaymentStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str

    gateway_payment_id: str | None

    status: str

    amount: Decimal

    currency: str

    completed_at: datetime | None