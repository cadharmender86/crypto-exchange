from datetime import datetime
from decimal import Decimal
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


class PaymentStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str

    gateway_payment_id: str | None

    status: str

    amount: Decimal

    currency: str

    completed_at: datetime | None