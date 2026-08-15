from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.order import CreateOrderRequest, OrderResponse
from app.services.matching_engine import MatchingEngine
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: CreateOrderRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        order = await OrderService.create_limit_order(
            db,
            user_id=current_user.id,
            base_asset_id=request.base_asset_id,
            quote_asset_id=request.quote_asset_id,
            side=request.side,
            price=request.price,
            quantity=request.quantity,
            client_order_id=request.client_order_id,
        )
        await MatchingEngine.match_order(db, order.id)
        await db.refresh(order)
        return order
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await OrderService.cancel_order(
            db,
            user_id=current_user.id,
            order_id=order_id,
        )
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
