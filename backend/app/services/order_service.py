from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.asset import Asset
from app.models.order import Order
from app.services.balance_service import BalanceService


class OrderService:
    CUSTOMER_ACCOUNT_TYPE = "CUSTOMER"
    OPEN_STATUS = "OPEN"

    @staticmethod
    async def create_limit_order(
        db: AsyncSession,
        *,
        user_id: UUID,
        base_asset_id: UUID,
        quote_asset_id: UUID,
        side: str,
        price: Decimal,
        quantity: Decimal,
        client_order_id: str | None = None,
    ) -> Order:
        if base_asset_id == quote_asset_id:
            raise ValueError("Base and quote assets must be different")

        side = side.upper()
        if side not in {"BUY", "SELL"}:
            raise ValueError("Invalid order side")

        price = Decimal(str(price))
        quantity = Decimal(str(quantity))
        if not price.is_finite() or price <= 0:
            raise ValueError("Price must be greater than zero")
        if not quantity.is_finite() or quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        if client_order_id:
            existing = await db.execute(
                select(Order).where(
                    Order.user_id == user_id,
                    Order.client_order_id == client_order_id,
                )
            )
            if existing.scalar_one_or_none() is not None:
                raise ValueError("Client order ID already exists")

        assets = await db.execute(
            select(Asset).where(Asset.id.in_([base_asset_id, quote_asset_id]))
        )
        asset_map = {asset.id: asset for asset in assets.scalars().all()}
        base_asset = asset_map.get(base_asset_id)
        quote_asset = asset_map.get(quote_asset_id)
        if base_asset is None or quote_asset is None:
            raise ValueError("Asset not found")
        if not base_asset.is_active or not quote_asset.is_active:
            raise ValueError("Asset is inactive")
        if not base_asset.trading_enabled or not quote_asset.trading_enabled:
            raise ValueError("Trading is disabled for this asset")

        required_asset_id = quote_asset_id if side == "BUY" else base_asset_id
        required_amount = price * quantity if side == "BUY" else quantity

        result = await db.execute(
            select(Account)
            .where(
                Account.user_id == user_id,
                Account.asset_id == required_asset_id,
                Account.account_type == OrderService.CUSTOMER_ACCOUNT_TYPE,
            )
            .with_for_update()
        )
        account = result.scalar_one_or_none()
        if account is None:
            raise ValueError("Required trading account does not exist")

        BalanceService._validate_account(account)
        await BalanceService.lock(account, required_amount)

        order = Order(
            user_id=user_id,
            base_asset_id=base_asset_id,
            quote_asset_id=quote_asset_id,
            client_order_id=client_order_id,
            side=side,
            order_type="LIMIT",
            status=OrderService.OPEN_STATUS,
            price=price,
            quantity=quantity,
            filled_quantity=Decimal("0"),
            remaining_quantity=quantity,
            fee_amount=Decimal("0"),
        )
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def list_orders(
        db: AsyncSession,
        *,
        user_id: UUID,
        status_filter: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        query = select(Order).where(Order.user_id == user_id)
        if status_filter:
            query = query.where(Order.status == status_filter)
        query = query.order_by(Order.created_at.desc()).limit(limit)

        result = await db.execute(query)
        orders = list(result.scalars().all())
        if not orders:
            return []

        asset_ids = {order.base_asset_id for order in orders}
        asset_ids.update(order.quote_asset_id for order in orders)
        assets_result = await db.execute(select(Asset).where(Asset.id.in_(asset_ids)))
        assets = {asset.id: asset for asset in assets_result.scalars().all()}

        return [
            OrderService._order_payload(order, assets)
            for order in orders
        ]

    @staticmethod
    async def get_order(
        db: AsyncSession,
        *,
        user_id: UUID,
        order_id: UUID,
    ) -> dict:
        result = await db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == user_id)
        )
        order = result.scalar_one_or_none()
        if order is None:
            raise ValueError("Order not found")

        assets_result = await db.execute(
            select(Asset).where(Asset.id.in_([order.base_asset_id, order.quote_asset_id]))
        )
        assets = {asset.id: asset for asset in assets_result.scalars().all()}
        return OrderService._order_payload(order, assets)

    @staticmethod
    def _order_payload(order: Order, assets: dict[UUID, Asset]) -> dict:
        base_asset = assets.get(order.base_asset_id)
        quote_asset = assets.get(order.quote_asset_id)
        amount = None
        if order.price is not None:
            amount = Decimal(str(order.price)) * Decimal(str(order.quantity))

        return {
            "id": order.id,
            "base_asset_id": order.base_asset_id,
            "quote_asset_id": order.quote_asset_id,
            "symbol": (
                f"{base_asset.symbol}/{quote_asset.symbol}"
                if base_asset and quote_asset
                else None
            ),
            "amount": amount,
            "client_order_id": order.client_order_id,
            "side": order.side,
            "order_type": order.order_type,
            "status": order.status,
            "price": order.price,
            "quantity": order.quantity,
            "filled_quantity": order.filled_quantity,
            "remaining_quantity": order.remaining_quantity,
            "average_execution_price": order.average_execution_price,
            "fee_amount": order.fee_amount,
            "fee_asset_id": order.fee_asset_id,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "cancelled_at": order.cancelled_at,
        }

    @staticmethod
    async def cancel_order(
        db: AsyncSession,
        *,
        user_id: UUID,
        order_id: UUID,
    ) -> Order:
        result = await db.execute(
            select(Order)
            .where(Order.id == order_id, Order.user_id == user_id)
            .with_for_update()
        )
        order = result.scalar_one_or_none()
        if order is None:
            raise ValueError("Order not found")
        if order.status != "OPEN":
            raise ValueError("Only open orders can be cancelled")

        required_asset_id = order.quote_asset_id if order.side == "BUY" else order.base_asset_id
        unlock_amount = (
            Decimal(str(order.price)) * Decimal(str(order.remaining_quantity))
            if order.side == "BUY"
            else Decimal(str(order.remaining_quantity))
        )

        result = await db.execute(
            select(Account)
            .where(
                Account.user_id == user_id,
                Account.asset_id == required_asset_id,
                Account.account_type == OrderService.CUSTOMER_ACCOUNT_TYPE,
            )
            .with_for_update()
        )
        account = result.scalar_one_or_none()
        if account is None:
            raise ValueError("Trading account does not exist")

        await BalanceService.unlock(account, unlock_amount)
        order.status = "CANCELLED"
        order.cancelled_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(order)
        return order
