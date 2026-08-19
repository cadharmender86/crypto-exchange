from decimal import Decimal
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.asset import Asset
from app.models.order import Order
from app.models.trade import Trade


class TradeService:
    @staticmethod
    async def list_history(
        db: AsyncSession,
        *,
        user_id: UUID,
        symbol: str | None = None,
        side: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        buy_order = aliased(Order)
        sell_order = aliased(Order)
        base_asset = aliased(Asset)
        quote_asset = aliased(Asset)

        query = (
            select(Trade, buy_order, sell_order, base_asset, quote_asset)
            .join(buy_order, buy_order.id == Trade.buy_order_id)
            .join(sell_order, sell_order.id == Trade.sell_order_id)
            .join(base_asset, base_asset.id == Trade.base_asset_id)
            .join(quote_asset, quote_asset.id == Trade.quote_asset_id)
            .where(or_(buy_order.user_id == user_id, sell_order.user_id == user_id))
            .order_by(Trade.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        if symbol:
            normalized_symbol = symbol.strip().upper()
            query = query.where(
                (base_asset.symbol + "/" + quote_asset.symbol) == normalized_symbol
            )

        result = await db.execute(query)
        rows = result.all()

        history: list[dict] = []
        for trade, buy, sell, base, quote in rows:
            trade_side = "BUY" if buy.user_id == user_id else "SELL"
            if side and trade_side != side.upper():
                continue

            history.append(
                {
                    "id": trade.id,
                    "symbol": f"{base.symbol}/{quote.symbol}",
                    "side": trade_side,
                    "price": trade.price,
                    "amount": trade.quantity,
                    "total": trade.quote_amount,
                    "fee": Decimal("0"),
                    "created_at": trade.created_at,
                }
            )

        return history
