from uuid import uuid4
from decimal import Decimal

import pytest_asyncio

from app.core.database import AsyncSessionLocal
from app.models.asset import Asset
from app.models.wallet import Wallet
from app.core.constants import AssetType


@pytest_asyncio.fixture
async def db():
    """
    Shared AsyncSession fixture for all repository/service tests.
    Each test gets its own transaction which is rolled back.
    """
    async with AsyncSessionLocal() as session:
        transaction = await session.begin()
        try:
            yield session
        finally:
            await transaction.rollback()
            await session.close()


@pytest_asyncio.fixture
async def asset(db):
    asset = Asset(
        id=uuid4(),
        symbol="TEST",
        name="Test Asset",
        asset_type=AssetType.CRYPTO,
        decimal_places=8,
        is_active=True,
        deposit_enabled=True,
        withdrawal_enabled=True,
        trading_enabled=True,
    )

    db.add(asset)
    await db.flush()

    return asset


@pytest_asyncio.fixture
async def wallet(db, asset):
    wallet = Wallet(
        id=uuid4(),
        user_id=uuid4(),
        asset_id=asset.id,
        balance_total=Decimal("1000"),
        balance_available=Decimal("1000"),
        balance_locked=Decimal("0"),
    )

    db.add(wallet)
    await db.flush()
    await db.refresh(wallet)

    return wallet