from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order import OrderSide, OrderStatus


class OrderBookRepository:
    """
    Repository responsible for retrieving
    executable orders from the order book.

    Matching Priority
    -----------------
    BUY taker  -> lowest SELL price first (FIFO).
    SELL taker -> highest BUY price first (FIFO).
    """

    @staticmethod
    async def get_matching_sell_orders(
        db: AsyncSession,
        *,
        trading_pair_id,
        taker_price,
    ) -> list[Order]:
        """
        Best asks for a BUY limit order.

        ORDER BY:
            price ASC,
            created_at ASC

        SKIP LOCKED prevents matching
        the same maker order twice.
        """

        result = await db.execute(
            select(Order)
            .where(
                Order.trading_pair_id == trading_pair_id,
                Order.side == OrderSide.SELL,
                Order.status.in_(
                    [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]
                ),
                Order.price <= taker_price,
            )
            .order_by(Order.price.asc(), Order.created_at.asc())
            .with_for_update(skip_locked=True)
        )

        return result.scalars().all()

    @staticmethod
    async def get_matching_buy_orders(
        db: AsyncSession,
        *,
        trading_pair_id,
        taker_price,
    ) -> list[Order]:
        """
        Best bids for a SELL limit order.

        ORDER BY:
            price DESC,
            created_at ASC
        """

        result = await db.execute(
            select(Order)
            .where(
                Order.trading_pair_id == trading_pair_id,
                Order.side == OrderSide.BUY,
                Order.status.in_(
                    [OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]
                ),
                Order.price >= taker_price,
            )
            .order_by(Order.price.desc(), Order.created_at.asc())
            .with_for_update(skip_locked=True)
        )

        return result.scalars().all()