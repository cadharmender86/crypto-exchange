from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.order import Order
from app.models.trade import Trade
from app.services.balance_service import BalanceService
from app.services.ledger_service import LedgerService


class MatchingEngine:
    """Match open limit orders and settle each fill atomically."""

    @staticmethod
    def _weighted_average(order: Order, price: Decimal, quantity: Decimal) -> Decimal:
        old_filled = Decimal(str(order.filled_quantity))
        old_average = Decimal(str(order.average_execution_price or 0))
        new_filled = old_filled + quantity
        if new_filled <= 0:
            return price
        return ((old_average * old_filled) + (price * quantity)) / new_filled

    @staticmethod
    async def match_order(db: AsyncSession, order_id: UUID) -> list[Trade]:
        trades: list[Trade] = []
        try:
            taker_result = await db.execute(
                select(Order).where(Order.id == order_id).with_for_update()
            )
            taker = taker_result.scalar_one_or_none()
            if taker is None:
                raise ValueError("Order not found")
            if taker.status != "OPEN" or Decimal(str(taker.remaining_quantity)) <= 0:
                return trades

            while taker.status == "OPEN" and Decimal(str(taker.remaining_quantity)) > 0:
                maker_query = select(Order).where(
                    Order.status == "OPEN",
                    Order.id != taker.id,
                    Order.user_id != taker.user_id,
                    Order.base_asset_id == taker.base_asset_id,
                    Order.quote_asset_id == taker.quote_asset_id,
                    Order.side != taker.side,
                    Order.remaining_quantity > 0,
                )
                if taker.side == "BUY":
                    maker_query = maker_query.where(Order.price <= taker.price).order_by(
                        Order.price.asc(), Order.created_at.asc(), Order.id.asc()
                    )
                else:
                    maker_query = maker_query.where(Order.price >= taker.price).order_by(
                        Order.price.desc(), Order.created_at.asc(), Order.id.asc()
                    )

                maker_result = await db.execute(maker_query.limit(1))
                candidate = maker_result.scalar_one_or_none()
                if candidate is None:
                    break

                locked_result = await db.execute(
                    select(Order)
                    .where(Order.id.in_([taker.id, candidate.id]))
                    .order_by(Order.id)
                    .with_for_update()
                )
                locked_orders = {order.id: order for order in locked_result.scalars().all()}
                taker = locked_orders[taker.id]
                maker = locked_orders[candidate.id]
                if maker.status != "OPEN" or Decimal(str(maker.remaining_quantity)) <= 0:
                    continue

                quantity = min(
                    Decimal(str(taker.remaining_quantity)),
                    Decimal(str(maker.remaining_quantity)),
                )
                price = Decimal(str(maker.price))
                quote_amount = quantity * price
                buy_order = taker if taker.side == "BUY" else maker
                sell_order = maker if taker.side == "BUY" else taker

                account_result = await db.execute(
                    select(Account)
                    .where(
                        Account.user_id.in_([buy_order.user_id, sell_order.user_id]),
                        Account.asset_id.in_([buy_order.base_asset_id, buy_order.quote_asset_id]),
                        Account.account_type == "CUSTOMER",
                    )
                    .order_by(Account.id)
                    .with_for_update()
                )
                accounts = account_result.scalars().all()
                account_map = {(account.user_id, account.asset_id): account for account in accounts}
                buyer_base = account_map.get((buy_order.user_id, buy_order.base_asset_id))
                buyer_quote = account_map.get((buy_order.user_id, buy_order.quote_asset_id))
                seller_base = account_map.get((sell_order.user_id, sell_order.base_asset_id))
                seller_quote = account_map.get((sell_order.user_id, sell_order.quote_asset_id))
                if not all([buyer_base, buyer_quote, seller_base, seller_quote]):
                    raise ValueError("Trading accounts required for settlement do not exist")

                buyer_order_price = Decimal(str(buy_order.price))
                buyer_reserved = buyer_order_price * quantity
                if buyer_reserved < quote_amount:
                    raise ValueError("Buyer reservation is insufficient for settlement")

                await BalanceService.consume_locked(buyer_quote, quote_amount)
                await BalanceService.consume_locked(seller_base, quantity)
                if buyer_reserved > quote_amount:
                    await BalanceService.unlock(buyer_quote, buyer_reserved - quote_amount)
                await BalanceService.credit(buyer_base, quantity)
                await BalanceService.credit(seller_quote, quote_amount)

                taker_average = MatchingEngine._weighted_average(taker, price, quantity)
                maker_average = MatchingEngine._weighted_average(maker, price, quantity)
                taker.filled_quantity = Decimal(str(taker.filled_quantity)) + quantity
                taker.remaining_quantity = Decimal(str(taker.quantity)) - Decimal(str(taker.filled_quantity))
                maker.filled_quantity = Decimal(str(maker.filled_quantity)) + quantity
                maker.remaining_quantity = Decimal(str(maker.quantity)) - Decimal(str(maker.filled_quantity))
                taker.status = ("FILLED" if taker.remaining_quantity == 0 else "PARTIALLY_FILLED")
                maker.status = ("FILLED" if maker.remaining_quantity == 0 else "PARTIALLY_FILLED")
                taker.average_execution_price = taker_average
                maker.average_execution_price = maker_average

                trade = Trade(
                    buy_order_id=buy_order.id,
                    sell_order_id=sell_order.id,
                    base_asset_id=buy_order.base_asset_id,
                    quote_asset_id=buy_order.quote_asset_id,
                    price=price,
                    quantity=quantity,
                    quote_amount=quote_amount,
                )
                db.add(trade)

                await LedgerService.create_transaction(
                    db,
                    transaction_type="TRADE",
                    entries=[
                        {"account_id": buyer_quote.id, "entry_type": "DEBIT", "amount": quote_amount},
                        {"account_id": seller_quote.id, "entry_type": "CREDIT", "amount": quote_amount},
                        {"account_id": seller_base.id, "entry_type": "DEBIT", "amount": quantity},
                        {"account_id": buyer_base.id, "entry_type": "CREDIT", "amount": quantity},
                    ],
                    description=f"Trade {buy_order.id} / {sell_order.id}",
                )
                trades.append(trade)
                await db.flush()
                if taker.status != "OPEN":
                    break

            await db.commit()
            return trades
        except Exception:
            await db.rollback()
            raise
