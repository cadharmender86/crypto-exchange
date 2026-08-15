from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.api.dependencies import get_db
from app.api.v1.admin_auth import require_permission
from app.models.admin import AdminUser
from app.models.asset import Asset
from app.models.order import Order
from app.models.user import User
from app.schemas.admin_orders import AdminOrderListResponse, AdminOrderResponse

router = APIRouter(prefix="/admin/orders", tags=["Admin Orders"])


def _row_to_response(row) -> AdminOrderResponse:
    order, user, base_asset, quote_asset, fee_asset = row
    return AdminOrderResponse(
        id=order.id,
        user_id=order.user_id,
        user_email=user.email,
        base_asset=base_asset.symbol,
        quote_asset=quote_asset.symbol,
        client_order_id=order.client_order_id,
        side=order.side,
        order_type=order.order_type,
        status=order.status,
        price=order.price,
        quantity=order.quantity,
        filled_quantity=order.filled_quantity,
        remaining_quantity=order.remaining_quantity,
        average_execution_price=order.average_execution_price,
        fee_amount=order.fee_amount,
        fee_asset=fee_asset.symbol if fee_asset else None,
        created_at=order.created_at,
        updated_at=order.updated_at,
        cancelled_at=order.cancelled_at,
    )


@router.get("", response_model=AdminOrderListResponse)
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: str | None = Query(None, min_length=1, max_length=255),
    status_filter: str | None = Query(None, alias="status", max_length=20),
    side: str | None = Query(None, max_length=4),
    _: AdminUser = Depends(require_permission("ORDER_READ")),
    db: AsyncSession = Depends(get_db),
):
    base_asset = aliased(Asset)
    quote_asset = aliased(Asset)
    fee_asset = aliased(Asset)

    filters = []
    if search:
        term = f"%{search.strip().lower()}%"
        filters.append(
            (func.lower(User.email).like(term))
            | (func.lower(Order.id.cast(String)).like(term))
            | (func.lower(func.coalesce(Order.client_order_id, "")).like(term))
        )
    if status_filter:
        filters.append(Order.status == status_filter.upper())
    if side:
        filters.append(Order.side == side.upper())

    count_result = await db.execute(
        select(func.count(Order.id))
        .join(User, User.id == Order.user_id)
        .where(*filters)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(Order, User, base_asset, quote_asset, fee_asset)
        .join(User, User.id == Order.user_id)
        .join(base_asset, base_asset.id == Order.base_asset_id)
        .join(quote_asset, quote_asset.id == Order.quote_asset_id)
        .outerjoin(fee_asset, fee_asset.id == Order.fee_asset_id)
        .where(*filters)
        .order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return AdminOrderListResponse(
        items=[_row_to_response(row) for row in result.all()],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{order_id}", response_model=AdminOrderResponse)
async def get_order(
    order_id: UUID,
    _: AdminUser = Depends(require_permission("ORDER_READ")),
    db: AsyncSession = Depends(get_db),
):
    base_asset = aliased(Asset)
    quote_asset = aliased(Asset)
    fee_asset = aliased(Asset)

    result = await db.execute(
        select(Order, User, base_asset, quote_asset, fee_asset)
        .join(User, User.id == Order.user_id)
        .join(base_asset, base_asset.id == Order.base_asset_id)
        .join(quote_asset, quote_asset.id == Order.quote_asset_id)
        .outerjoin(fee_asset, fee_asset.id == Order.fee_asset_id)
        .where(Order.id == order_id)
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return _row_to_response(row)
