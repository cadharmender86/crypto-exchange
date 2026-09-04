from app.core.config import settings
from app.core.database import get_db
from app.services.payment_service import PaymentService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter, Header, HTTPException, Request

from app.services.webhook_service import CashfreeWebhookService

router = APIRouter(prefix="/payments", tags=["Cashfree Webhooks"])


@router.post("/webhook")
async def cashfree_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_webhook_signature: str = Header(alias="x-webhook-signature"),
    x_webhook_timestamp: str = Header(alias="x-webhook-timestamp"),
):
    body = await request.body()

    # Skip signature verification only in local development.
    if settings.cashfree_verify_webhook_signature:
        is_valid = CashfreeWebhookService.verify_signature(
            body=body,
            signature=x_webhook_signature,
            timestamp=x_webhook_timestamp,
        )

        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature.",
            )
        
    # is_valid = CashfreeWebhookService.verify_signature(
    #     body=body,
    #     signature=x_webhook_signature,
    #     timestamp=x_webhook_timestamp,
    # )

    # if not is_valid:
    #     raise HTTPException(
    #         status_code=401,
    #         detail="Invalid webhook signature.",
    #     )

    # LOCAL TEST ONLY (Phase 7.4.2)
    # Skip Cashfree signature verification.

    # is_valid = True

    payload = await request.json()

    service = PaymentService(db)

    payment_order = await service.process_cashfree_webhook(payload)

    print("Cashfree Webhook Received")
    print(payload)

    return {
        "status": "processed",
        "order_id": payment_order.gateway_order_id,
        "payment_status": payment_order.status.value,
    }