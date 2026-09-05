from decimal import Decimal
from datetime import datetime, UTC
from uuid import UUID

# from app.models import payment_order
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.asset import Asset
# from app.models.fiat_account import FiatAccount
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
# from app.models.payment_order import (
    # PaymentOrder,
    # PaymentOrderStatus,
# )
# from app.models.fiat_transaction import (
    # FiatTransaction,
    # FiatTransactionType,
    # FiatTransactionStatus,
# )

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


        #Find INR asset first.
        asset_result = await self.db.execute(
            select(Asset).where(Asset.symbol == "INR")
        )

        inr_asset = asset_result.scalar_one_or_none()

        if inr_asset is None:
            raise ValueError("INR asset not found.")

        # Find user's INR fiat account and lock it
        result = await self.db.execute(
            select(Account)
            .where(
                Account.user_id == payment_order.user_id,
                Account.asset_id == inr_asset.id,
                Account.account_type == "CUSTOMER",
            )
           .with_for_update()
        )

        account = result.scalar_one_or_none()

        if account is None:
            raise ValueError("INR account not found.")

        if payment_status == "SUCCESS":
            print("=== CASHFREE SUCCESS WEBHOOK ===")
            print("Order:", gateway_order_id)
            print("Amount:", payment_order.amount)

            print("INR balance BEFORE:", account.available_balance)

            # Credit INR balance atomically
            await BalanceService.credit(
                account,
                payment_order.amount,
            )

            print("INR balance AFTER :", account.available_balance)

            #Ledger entry
            # fiat_transaction = FiatTransaction(
            #     fiat_account_id=account.id,
            #     user_id=payment_order.user_id,
            #     transaction_type=FiatTransactionType.INR_DEPOSIT,
            #     amount=payment_order.amount,
            #     balance_after=account.available_balance,
            #     reference_type="CASHFREE_PAYMENT",
            #     reference_id=cf_payment_id,
            #     idempotency_key=f"CASHFREE:{cf_payment_id}",
            #     status=FiatTransactionStatus.COMPLETED,
            #     description=f"Cashfree deposit: {gateway_order_id}",
            # )  

            # self.db.add(fiat_transaction)
            # TODO (Phase 8): Replace FiatTransaction with unified wallet ledger.
            # pass
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

    async def get_payment_history(self, user_id: UUID):
        result = await self.db.execute(
            select(PaymentOrder)
            .where(PaymentOrder.user_id == user_id)
            .order_by(PaymentOrder.created_at.desc())
        )

        return result.scalars().all()