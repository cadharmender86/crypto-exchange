from decimal import Decimal
from datetime import datetime, UTC

# from app.models import payment_order
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fiat_account import FiatAccount
# from app.models.payment_order import PaymentOrderStatus
from app.services.balance_service import BalanceService
from app.models.payment_order import (
    PaymentGateway,
    PaymentOrder,
    PaymentOrderStatus,
)
from uuid import uuid4
from app.models.user import User
from app.services.gateways.cashfree import CashfreeGateway
from app.models.payment_order import (
    PaymentOrder,
    PaymentOrderStatus,
)
from app.models.fiat_transaction import (
    FiatTransaction,
    FiatTransactionType,
    FiatTransactionStatus,
)

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

    # ----------------------------------
    # Verify webhook payment event
# ----------------------------------

    async def process_cashfree_webhook(self, payload: dict):
        payment = payload["data"]["payment"]
        order = payload["data"]["order"]

        gateway_order_id = order["order_id"]
        cf_payment_id = payment["cf_payment_id"]
        payment_status = payment["payment_status"]

        result = await self.db.execute(
            select(PaymentOrder).where(
                PaymentOrder.gateway_order_id == gateway_order_id,
            )
        )

        payment_order = result.scalar_one_or_none()

        if payment_order is None:
            raise ValueError("Payment order not found.")

        # Duplicate webhook protection
        if payment_order.status == PaymentOrderStatus.SUCCESS:
            return payment_order


        # Find user's INR fiat account and lock it
        result = await self.db.execute(
            select(FiatAccount)
            .where(
                FiatAccount.user_id == payment_order.user_id,
                FiatAccount.currency == "INR",
            )
           .with_for_update()
        )

        fiat_account = result.scalar_one_or_none()

        if fiat_account is None:
            raise ValueError("Fiat account not found.")

        if payment_status == "SUCCESS":

            # Credit INR balance atomically
            await BalanceService.credit(
                fiat_account,
                payment_order.amount,
            )

            #Ledger entry
            fiat_transaction = FiatTransaction(
                fiat_account_id=fiat_account.id,
                user_id=payment_order.user_id,
                transaction_type=FiatTransactionType.INR_DEPOSIT,
                amount=payment_order.amount,
                balance_after=fiat_account.available_balance,
                reference_type="CASHFREE_PAYMENT",
                reference_id=cf_payment_id,
                idempotency_key=f"CASHFREE:{cf_payment_id}",
                status=FiatTransactionStatus.COMPLETED,
                description=f"Cashfree deposit: {gateway_order_id}",
            )  

            self.db.add(fiat_transaction)

            # Update payment order first
            payment_order.status = PaymentOrderStatus.SUCCESS
            payment_order.gateway_payment_id = cf_payment_id
            payment_order.completed_at = datetime.now(UTC)
            

        elif payment_status == "FAILED":
            payment_order.status = PaymentOrderStatus.FAILED
            
        elif payment_status == "CANCELLED":
            payment_order.status = PaymentOrderStatus.CANCELLED

        else:
            payment_order.status = PaymentOrderStatus.PENDING

        await self.db.commit()
        await self.db.refresh(payment_order)

        return payment_order