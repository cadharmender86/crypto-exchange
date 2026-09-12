from decimal import Decimal

import pytest

from app.repositories.wallet_repository import WalletRepository
from app.core.exchange_errors import InsufficientBalanceError

@pytest.mark.asyncio
async def test_reserve_balance(db, wallet):
    wallet.balance_available = Decimal("1000")
    wallet.balance_locked = Decimal("0")

    updated = await WalletRepository.reserve_balance(
        db,
        wallet=wallet,
        amount=Decimal("250"),
    )

    assert updated.balance_available == Decimal("750")
    assert updated.balance_locked == Decimal("250")

@pytest.mark.asyncio
async def test_reserve_balance_insufficient(db, wallet):
    wallet.balance_available = Decimal("50")
    wallet.balance_locked = Decimal("0")

    with pytest.raises(InsufficientBalanceError):
        await WalletRepository.reserve_balance(
            db,
            wallet=wallet,
            amount=Decimal("100"),
        )

@pytest.mark.asyncio
async def test_release_balance(db, wallet):
    wallet.balance_available = Decimal("500")
    wallet.balance_locked = Decimal("300")

    updated = await WalletRepository.release_balance(
        db,
        wallet=wallet,
        amount=Decimal("100"),
    )

    assert updated.balance_available == Decimal("600")
    assert updated.balance_locked == Decimal("200")

@pytest.mark.asyncio
async def test_consume_locked_balance(db, wallet):
    wallet.balance_available = Decimal("500")
    wallet.balance_locked = Decimal("250")

    updated = await WalletRepository.consume_locked_balance(
        db,
        wallet=wallet,
        amount=Decimal("250"),
    )

    assert updated.balance_locked == Decimal("0")
    assert updated.balance_available == Decimal("500")                