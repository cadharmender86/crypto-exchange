from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment_order import (
    PaymentGateway,
    PaymentOrder,
    PaymentOrderStatus,
)
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

        gateway_response = self.gateway.create_payment_order(
            user_id=str(user.id),
            email=user.email,
            phone="9999999999",     # Temporary sandbox number
            amount=float(amount),
        )

        payment_order = PaymentOrder(
            user_id=user.id,
            gateway=PaymentGateway.CASHFREE,
            gateway_order_id=gateway_response["gateway_order_id"],
            payment_session_id=gateway_response["payment_session_id"],
            amount=amount,
            currency="INR",
            status=PaymentOrderStatus.PENDING,
            expires_at=gateway_response["expires_at"],
        )

        self.db.add(payment_order)
        await self.db.commit()
        await self.db.refresh(payment_order)

        return payment_order