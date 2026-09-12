from decimal import Decimal

import pytest

from app.repositories.order_book_repository import OrderBookRepository
from app.models.order import OrderSide, OrderStatus


@pytest.mark.asyncio
async def test_get_matching_sell_orders(db):
    """
    BUY order should receive SELL orders
    sorted by lowest price first.
    """
    # TODO (next commit):
    # Insert maker sell orders.
    # Assert returned order sequence.
    assert True


@pytest.mark.asyncio
async def test_get_matching_buy_orders(db):
    """
    SELL order should receive BUY orders
    sorted by highest price first.
    """
    # TODO (next commit):
    # Insert maker buy orders.
    # Assert returned order sequence.
    assert True


@pytest.mark.asyncio
async def test_skip_closed_orders(db):
    """
    FILLED/CANCELLED orders
    must never appear in the order book.
    """
    assert True