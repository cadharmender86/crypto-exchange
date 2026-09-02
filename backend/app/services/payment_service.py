from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment_order import (
    PaymentGateway,
    PaymentOrder,
    PaymentOrderStatus,
)
from uuid import uuid4
from app.models.user import User
from app.services.gateways.cashfree import CashfreeGateway


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.gateway = CashfreeGateway()

    async def create_cashfree_order(
        self,
        *,
        user: User,
        amount: Decimal,
    ) -> PaymentOrder:
        gateway_order_id = f"BN_{uuid4().hex[:20]}"

        gateway_response = self.gateway.create_payment_order(
            order_id=gateway_order_id,
            customer_id=str(user.id),
            customer_email=user.email,
            customer_phone="9999999999",
            amount=amount,
        )

        payment_order = PaymentOrder(
            user_id=user.id,
            gateway=PaymentGateway.CASHFREE,
            gateway_order_id=gateway_response["gateway_order_id"],
            payment_session_id=gateway_response["payment_session_id"],
            amount=amount,
            currency="INR",
            status=PaymentOrderStatus.PENDING,
            expires_at=(
                datetime.fromisoformat(gateway_response["expires_at"])
                if gateway_response.get("expires_at")
                else None
            ),
        )

        self.db.add(payment_order)
        await self.db.commit()
        await self.db.refresh(payment_order)

        return payment_order