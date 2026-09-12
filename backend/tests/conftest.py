from uuid import uuid4
from decimal import Decimal

import pytest_asyncio

from app.core.database import AsyncSessionLocal
from app.models.asset import Asset
from app.models.account import Account
from app.core.constants import AssetType
from app.models.user import User

@pytest_asyncio.fixture
async def db():
    """
    Shared AsyncSession fixture for all repository/service tests.
    Each test gets its own transaction which is rolled back.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


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
async def user(db):
    user = User(
        id=uuid4(),
        email=f"test-{uuid4().hex[:8]}@bitnova.test",
        password_hash="dummy_hash",
        is_active=True,
        is_verified=True,
        two_factor_enabled=False,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user


@pytest_asyncio.fixture
async def account(db, asset, user):
    account = Account(
        id=uuid4(),
        user_id=user.id,
        asset_id=asset.id,
        account_type="CUSTOMER",
        available_balance=Decimal("1000"),
        locked_balance=Decimal("0"),
        status="ACTIVE",
    )

    db.add(account)
    await db.flush()
    await db.refresh(account)

    return account