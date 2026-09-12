from decimal import Decimal

import pytest

from app.repositories.account_repository import AccountRepository
from app.core.exchange_errors import InsufficientBalanceError


@pytest.mark.asyncio
async def test_reserve_balance(db, account):
    account.available_balance = Decimal("1000")
    account.locked_balance = Decimal("0")

    updated = await AccountRepository.reserve_balance(
        db,
        account=account,
        amount=Decimal("250"),
    )

    assert updated.available_balance == Decimal("750")
    assert updated.locked_balance == Decimal("250")


@pytest.mark.asyncio
async def test_reserve_balance_insufficient(db, account):
    account.available_balance = Decimal("50")
    account.locked_balance = Decimal("0")

    with pytest.raises(InsufficientBalanceError):
        await AccountRepository.reserve_balance(
            db,
            account=account,
            amount=Decimal("100"),
        )


@pytest.mark.asyncio
async def test_release_balance(db, account):
    account.available_balance = Decimal("500")
    account.locked_balance = Decimal("300")

    updated = await AccountRepository.release_balance(
        db,
        account=account,
        amount=Decimal("100"),
    )

    assert updated.available_balance == Decimal("600")
    assert updated.locked_balance == Decimal("200")


@pytest.mark.asyncio
async def test_consume_locked_balance(db, account):
    account.available_balance = Decimal("500")
    account.locked_balance = Decimal("250")

    updated = await AccountRepository.consume_locked_balance(
        db,
        account=account,
        amount=Decimal("250"),
    )

    assert updated.locked_balance == Decimal("0")
    assert updated.available_balance == Decimal("500")