from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.order import Order
from app.models.trading_pair import TradingPair


class OrderRepository:
    """
    Repository for Spot Orders.

    This layer contains ALL database queries related to orders.
    """

    # -------------------------------------------------------
    # CREATE
    # -------------------------------------------------------

    @staticmethod
    async def create(
        db: AsyncSession,
        order: Order,
    ) -> Order:

        db.add(order)

        await db.flush()
        await db.refresh(order)

        return order

    # -------------------------------------------------------
    # READ
    # -------------------------------------------------------

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        order_id: UUID,
    ) -> Order | None:

        result = await db.execute(
            select(Order)
            .options(joinedload(Order.trading_pair))
            .where(Order.id == order_id)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def list_user_orders(
        db: AsyncSession,
        *,
        user_id: UUID,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Order]:

        query = (
            select(Order)
            .options(joinedload(Order.trading_pair))
            .where(Order.user_id == user_id)
            .order_by(desc(Order.created_at))
            .limit(limit)
            .offset(offset)
        )

        if status:
            query = query.where(Order.status == status.upper())

        result = await db.execute(query)

        return list(result.scalars().all())

    # -------------------------------------------------------
    # OPEN ORDERS
    # -------------------------------------------------------

    @staticmethod
    async def list_open_orders(
        db: AsyncSession,
        *,
        trading_pair_id: UUID,
    ) -> list[Order]:

        result = await db.execute(
            select(Order)
            .where(
                and_(
                    Order.trading_pair_id == trading_pair_id,
                    Order.status.in_(
                        [
                            "NEW",
                            "PARTIALLY_FILLED",
                        ]
                    ),
                )
            )
            .order_by(desc(Order.created_at))
        )

        return list(result.scalars().all())

    # -------------------------------------------------------
    # ORDER BOOK
    # -------------------------------------------------------

    @staticmethod
    async def list_order_book_side(
        db: AsyncSession,
        *,
        trading_pair_id: UUID,
        side: str,
        limit: int = 100,
    ) -> list[Order]:

        query = (
            select(Order)
            .where(
                and_(
                    Order.trading_pair_id == trading_pair_id,
                    Order.side == side.upper(),
                    Order.status.in_(
                        [
                            "NEW",
                            "PARTIALLY_FILLED",
                        ]
                    ),
                )
            )
            .limit(limit)
        )

        # BUY -> Highest price first.
        if side.upper() == "BUY":
            query = query.order_by(
                desc(Order.price),
                asc(Order.created_at),
            )

        # SELL -> Lowest price first.
        else:
            query = query.order_by(
                asc(Order.price),
                asc(Order.created_at),
            )

        result = await db.execute(query)

        return list(result.scalars().all())

    @staticmethod
    async def lock_matching_orders(
        db: AsyncSession,
        *,
        trading_pair_id: UUID,
        side: str,
        limit: int = 100,
    ) -> list[Order]:

        query = (
            select(Order)
            .where(
                and_(
                    Order.trading_pair_id == trading_pair_id,
                    Order.side == side.upper(),
                    Order.status.in_(
                        [
                            "NEW",
                            "PARTIALLY_FILLED",
                        ]
                    ),
                )
            )
            .with_for_update(skip_locked=True)
            .limit(limit)
        )

        if side.upper() == "BUY":
            query = query.order_by(
                desc(Order.price),
                asc(Order.created_at),
            )
        else:
            query = query.order_by(
                asc(Order.price),
                asc(Order.created_at),
            )

        result = await db.execute(query)

        return list(result.scalars().all())

    # -------------------------------------------------------
    # UPDATE EXECUTION
    # -------------------------------------------------------

    @staticmethod
    async def update_execution(
        db: AsyncSession,
        *,
        order: Order,
        executed_quantity: Decimal,
        average_price: Decimal,
        quote_amount: Decimal,
        fee_amount: Decimal,
        status: str,
    ) -> Order:

        order.executed_quantity = executed_quantity
        order.remaining_quantity = (
            order.quantity - executed_quantity
        )
        order.average_price = average_price
        order.quote_amount = quote_amount
        order.fee_amount = fee_amount
        order.status = status

        await db.flush()
        await db.refresh(order)

        return order

    # -------------------------------------------------------
    # CANCEL
    # -------------------------------------------------------

    @staticmethod
    async def cancel_order(
        db: AsyncSession,
        *,
        order: Order,
        reason: str,
    ) -> Order:

        order.status = "CANCELLED"
        order.cancel_reason = reason

        await db.flush()
        await db.refresh(order)

        return order