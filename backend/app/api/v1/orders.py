from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.order import CreateOrderRequest, OrderResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/open", response_model=list[OrderResponse])
async def get_open_orders(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await OrderService.list_orders(
        db,
        user_id=current_user.id,
        status_filter=OrderService.OPEN_STATUS,
    )


@router.get("", response_model=list[OrderResponse])
async def get_orders(
    status_filter: str | None = Query(default=None, alias="status"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if status_filter is not None and status_filter.strip() == "":
        status_filter = None
    return await OrderService.list_orders(
        db,
        user_id=current_user.id,
        status_filter=status_filter,
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: CreateOrderRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await OrderService.create_limit_order(
            db,
            user_id=current_user.id,
            base_asset_id=request.base_asset_id,
            quote_asset_id=request.quote_asset_id,
            side=request.side,
            price=request.price,
            quantity=request.quantity,
            client_order_id=request.client_order_id,
        )
    except ValueError as exc:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await OrderService.get_order(
            db,
            user_id=current_user.id,
            order_id=order_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


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
