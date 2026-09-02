from decimal import Decimal
from uuid import uuid4

from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
# from cashfree_pg.models.env import Env

from app.core.config import settings


class CashfreeGateway:
    """Cashfree Payment Gateway Client."""

    def __init__(self):
        # Cashfree.XClientId = settings.cashfree_app_id
        # Cashfree.XClientSecret = settings.cashfree_secret_key
        environment  = (
            Cashfree.SANDBOX
            if settings.cashfree_environment.lower() == "sandbox"
            else Cashfree.PRODUCTION
        )

        self.client = Cashfree(
            XEnvironment=environment,
            XClientId=settings.cashfree_app_id,
            XClientSecret=settings.cashfree_secret_key,
        )

    def create_payment_order(
        self,
        order_id: str,
        customer_id: str,
        customer_email: str,
        customer_phone: str,
        amount: Decimal,
    ):
        request = CreateOrderRequest(
            order_amount=float(amount),
            order_currency="INR",
            order_id=order_id,
            customer_details=CustomerDetails(
                customer_id=customer_id,
                customer_email=customer_email,
                customer_phone=customer_phone,
            ),
            order_meta=OrderMeta(
                return_url=f"{settings.frontend_url}/wallet/deposit/success?order_id={order_id}"
            )
        )

        # Cashfree SDK v6.0.1
        api_response = self.client.PGCreateOrder(
            create_order_request=request
        )

        order = api_response.data

        return {
            "gateway_order_id": order.order_id,
            "payment_session_id": order.payment_session_id,
            "order_status": order.order_status,
            "expires_at": order.order_expiry_time,
        }