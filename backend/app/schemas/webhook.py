from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CashfreePaymentData(BaseModel):
    cf_payment_id: str
    payment_status: str
    payment_amount: Decimal
    payment_currency: str
    payment_time: datetime


class CashfreeOrderData(BaseModel):
    order_id: str
    order_amount: Decimal
    order_currency: str


class CashfreeWebhookPayload(BaseModel):
    type: str
    data: dict