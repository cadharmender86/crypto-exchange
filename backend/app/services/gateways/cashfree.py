from datetime import datetime, timedelta, UTC
from uuid import uuid4

from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta

from app.core.config import settings


class CashfreeGateway:
    """Cashfree Payment Gateway Client."""

    def __init__(self):
        Cashfree.XClientId = settings.cashfree_app_id
        Cashfree.XClientSecret = settings.cashfree_secret_key
        Cashfree.XEnvironment = settings.cashfree_env

    def create_payment_order(
        self,
        *,
        user_id: str,
        email: str,
        phone: str,
        amount: float,
    ) -> dict:
        order_id = f"BN-{uuid4().hex[:24]}"

        expires_at = datetime.now(UTC) + timedelta(minutes=30)

        request = CreateOrderRequest(
            order_id=order_id,
            order_amount=amount,
            order_currency="INR",
            customer_details=CustomerDetails(
                customer_id=user_id,
                customer_email=email,
                customer_phone=phone,
            ),
            order_meta=OrderMeta(
                return_url=f"{settings.frontend_url}/wallet/deposit/success?order_id={order_id}"
            ),
            order_expiry_time=expires_at.isoformat(),
        )

        response = Cashfree().PGCreateOrder(request)

        return {
            "gateway_order_id": response.data.order_id,
            "payment_session_id": response.data.payment_session_id,
            "expires_at": expires_at,
        }