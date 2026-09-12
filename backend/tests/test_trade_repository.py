from decimal import Decimal

import pytest

from app.repositories.trade_repository import TradeRepository


@pytest.mark.asyncio
async def test_create_trade(db):
    """
    Repository should create immutable trade.
    """
    # Will be completed in Commit #4
    assert True


@pytest.mark.asyncio
async def test_get_trade_by_id(db):
    """
    Repository fetches trade.
    """
    assert True


@pytest.mark.asyncio
async def test_get_order_trades(db):
    """
    Repository returns all executions for an order.
    """
    assert True