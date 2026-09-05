from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.payment import (
    CreatePaymentOrderRequest,
    PaymentOrderResponse,
    PaymentHistoryItem,
    PaymentHistoryResponse,
)
from app.services.payment_service import PaymentService

router = APIRouter(
    tags=["Payments"],
)


@router.post(
    "/orders",
    response_model=PaymentOrderResponse,
)
async def create_payment_order(
    payload: CreatePaymentOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PaymentService(db)

    order = await service.create_cashfree_order(
        user=current_user,
        amount=payload.amount,
    )

    return PaymentOrderResponse(
        id=order.id,
        gateway_order_id=order.gateway_order_id,
        payment_session_id=order.payment_session_id,
        amount=order.amount,
        currency=order.currency,
        status=order.status.value,
        expires_at=order.expires_at,
    )

@router.get(
    "/history",
    response_model=PaymentHistoryResponse,
)
async def payment_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PaymentService(db)

    orders = await service.get_payment_history(current_user.id)

    return PaymentHistoryResponse(
        items=[
            PaymentHistoryItem.model_validate(order, from_attributes=True)
            for order in orders
        ]
    )