from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trade import Trade


class TradeRepository:
    """
    Repository responsible for Trade persistence.

    Trades are immutable execution records.
    """

    @staticmethod
    async def create_trade(
        db: AsyncSession,
        *,
        buy_order,
        sell_order,
        execution_price,
        execution_quantity,
    ) -> Trade:
        """
        Create immutable trade record.

        Execution price is always the maker price.
        """

        trade = Trade(
            buy_order_id=buy_order.id,
            sell_order_id=sell_order.id,
            buyer_user_id=buy_order.user_id,
            seller_user_id=sell_order.user_id,
            base_asset_id=buy_order.base_asset_id,
            quote_asset_id=buy_order.quote_asset_id,
            price=execution_price,
            quantity=execution_quantity,
            quote_amount=execution_price * execution_quantity,
        )

        db.add(trade)

        await db.flush()
        await db.refresh(trade)

        return trade

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        trade_id: UUID,
    ) -> Trade | None:
        """
        Fetch trade by primary key.
        """

        result = await db.execute(
            select(Trade).where(
                Trade.id == trade_id,
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_order_trades(
        db: AsyncSession,
        order_id: UUID,
    ) -> list[Trade]:
        """
        Return all trades executed for an order.
        """

        result = await db.execute(
            select(Trade)
            .where(
                or_(
                    Trade.buy_order_id == order_id,
                    Trade.sell_order_id == order_id,
                )
            )
            .order_by(Trade.created_at.asc())
        )

        return list(result.scalars().all())