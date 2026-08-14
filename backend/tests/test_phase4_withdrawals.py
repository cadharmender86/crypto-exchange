import asyncio
from decimal import Decimal
from pathlib import Path
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.models.account import Account
from app.models.asset import Asset
from app.models.ledger_entry import LedgerEntry
from app.models.ledger_transaction import LedgerTransaction
from app.models.user import User
from app.models.withdrawal import Withdrawal
from app.services.withdrawal_service import WithdrawalService
from unittest.mock import AsyncMock, patch


engine = create_async_engine(settings.database_url)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def test_valid_withdrawal_creation(db):
    print("\n[1] Valid withdrawal creation")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    customer_result = await db.execute(
        select(Account).where(
            Account.user_id == user.id,
            Account.asset_id == asset.id,
            Account.account_type == "CUSTOMER",
        )
    )
    customer = customer_result.scalar_one_or_none()

    if customer is None:
        raise AssertionError("Customer account does not exist")

    treasury_result = await db.execute(
        select(Account).where(
            Account.asset_id == asset.id,
            Account.account_type == "SYSTEM_TREASURY",
        )
    )
    treasury = treasury_result.scalar_one_or_none()

    if treasury is None:
        raise AssertionError("System treasury account does not exist")

    if not asset.withdrawal_enabled:
        raise AssertionError(
            "USDT withdrawals are disabled in the test database"
        )

    amount = Decimal("10")
    available_before = Decimal(
        str(customer.available_balance)
    )
    locked_before = Decimal(
        str(customer.locked_balance)
    )

    if available_before < amount:
        raise AssertionError(
            "Customer does not have enough available balance"
        )

    withdrawal = await WithdrawalService.create_pending_withdrawal(
        db,
        user_id=user.id,
        asset_id=asset.id,
        network="TRON",
        destination_address="TTestWithdrawalDestination123",
        amount=amount,
        idempotency_key="phase43-withdrawal-test-1",
    )

    if withdrawal.status != WithdrawalService.PENDING:
        raise AssertionError(
            f"Expected PENDING, got {withdrawal.status}"
        )

    if withdrawal.amount != amount:
        raise AssertionError(
            f"Unexpected amount: {withdrawal.amount}"
        )

    if withdrawal.account_id != customer.id:
        raise AssertionError(
            "Withdrawal is linked to the wrong customer account"
        )

    if withdrawal.ledger_transaction_id is None:
        raise AssertionError(
            "Withdrawal has no ledger transaction"
        )

    await db.flush()

    await db.refresh(customer)

    available_after = Decimal(
        str(customer.available_balance)
    )
    locked_after = Decimal(
        str(customer.locked_balance)
    )

    if available_after != available_before - amount:
        raise AssertionError(
            "Available balance was not reduced correctly"
        )

    if locked_after != locked_before + amount:
        raise AssertionError(
            "Locked balance was not increased correctly"
        )

    transaction_result = await db.execute(
        select(LedgerTransaction).where(
            LedgerTransaction.id
            == withdrawal.ledger_transaction_id
        )
    )
    transaction = transaction_result.scalar_one()

    if transaction.transaction_type != "WITHDRAWAL":
        raise AssertionError(
            f"Unexpected transaction type: "
            f"{transaction.transaction_type}"
        )

    entries_result = await db.execute(
        select(LedgerEntry).where(
            LedgerEntry.transaction_id == transaction.id
        )
    )
    entries = list(entries_result.scalars())

    if len(entries) != 2:
        raise AssertionError(
            f"Expected 2 ledger entries, got {len(entries)}"
        )

    debit = next(
        entry
        for entry in entries
        if entry.entry_type == "DEBIT"
    )

    credit = next(
        entry
        for entry in entries
        if entry.entry_type == "CREDIT"
    )

    if debit.account_id != customer.id:
        raise AssertionError(
            "Customer must be the withdrawal debit account"
        )

    if credit.account_id != treasury.id:
        raise AssertionError(
            "Treasury must be the withdrawal credit account"
        )

    if debit.amount != amount or credit.amount != amount:
        raise AssertionError(
            "Withdrawal ledger entries are not balanced"
        )

    await db.rollback()

async def test_withdrawal_is_idempotent(db):
    print("\n[2] Withdrawal idempotency")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    idempotency_key = "phase43-withdrawal-idempotency-test"

    withdrawal_1 = await WithdrawalService.create_pending_withdrawal(
        db,
        user_id=user.id,
        asset_id=asset.id,
        network="TRON",
        destination_address="TTestWithdrawalDestination123",
        amount=Decimal("5"),
        idempotency_key=idempotency_key,
    )

    await db.flush()

    withdrawal_2 = await WithdrawalService.create_pending_withdrawal(
        db,
        user_id=user.id,
        asset_id=asset.id,
        network="TRON",
        destination_address="TTestWithdrawalDestination123",
        amount=Decimal("5"),
        idempotency_key=idempotency_key,
    )

    if withdrawal_1.id != withdrawal_2.id:
        raise AssertionError(
            "Idempotent request created a second withdrawal"
        )

    withdrawal_count_result = await db.execute(
        select(Withdrawal).where(
            Withdrawal.user_id == user.id,
            Withdrawal.idempotency_key == idempotency_key,
        )
    )

    withdrawals = list(withdrawal_count_result.scalars())

    if len(withdrawals) != 1:
        raise AssertionError(
            f"Expected exactly 1 withdrawal, got {len(withdrawals)}"
        )

    await db.rollback()

async def test_idempotency_key_cannot_change_parameters(db):
    print("\n[3] Idempotency key cannot change withdrawal parameters")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    idempotency_key = "phase43-withdrawal-parameter-mismatch"

    await WithdrawalService.create_pending_withdrawal(
        db,
        user_id=user.id,
        asset_id=asset.id,
        network="TRON",
        destination_address="TTestWithdrawalDestination123",
        amount=Decimal("5"),
        idempotency_key=idempotency_key,
    )

    await db.flush()

    try:
        await WithdrawalService.create_pending_withdrawal(
            db,
            user_id=user.id,
            asset_id=asset.id,
            network="TRON",
            destination_address="TDifferentDestination456",
            amount=Decimal("10"),
            idempotency_key=idempotency_key,
        )
    except ValueError as exc:
        if "Idempotency key already used" not in str(exc):
            raise AssertionError(
                f"Unexpected error: {exc}"
            )
    else:
        raise AssertionError(
            "Expected parameter mismatch to be rejected"
        )

    await db.rollback()

async def test_insufficient_balance_does_not_lock_funds(db):
    print("\n[4] Insufficient balance does not lock funds")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    customer_result = await db.execute(
        select(Account).where(
            Account.user_id == user.id,
            Account.asset_id == asset.id,
            Account.account_type == "CUSTOMER",
        )
    )
    customer = customer_result.scalar_one()

    customer_id = customer.id

    available_before = Decimal(
        str(customer.available_balance)
    )
    locked_before = Decimal(
        str(customer.locked_balance)
    )

    try:
        await WithdrawalService.create_pending_withdrawal(
            db,
            user_id=user.id,
            asset_id=asset.id,
            network="TRON",
            destination_address="TTestWithdrawalDestination789",
            amount=available_before + Decimal("1"),
            idempotency_key="phase43-withdrawal-insufficient-test",
        )
    except ValueError as exc:
        if "Insufficient available balance" not in str(exc):
            raise AssertionError(
                f"Unexpected error: {exc}"
            )
    else:
        raise AssertionError(
            "Expected insufficient balance to be rejected"
        )

    await db.rollback()

    async with SessionLocal() as verify_db:
        customer_result = await verify_db.execute(
            select(Account).where(
                Account.id == customer_id
            )
        )
        customer_after = customer_result.scalar_one()

        if Decimal(str(customer_after.available_balance)) != available_before:
            raise AssertionError(
                "Available balance changed after rejected withdrawal"
            )

        if Decimal(str(customer_after.locked_balance)) != locked_before:
            raise AssertionError(
                "Locked balance changed after rejected withdrawal"
            )

async def test_withdrawal_disabled_asset_is_rejected(db):
    print("\n[5] Withdrawal disabled asset is rejected")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    original_value = asset.withdrawal_enabled

    try:
        asset.withdrawal_enabled = False
        await db.flush()

        try:
            await WithdrawalService.create_pending_withdrawal(
                db,
                user_id=user.id,
                asset_id=asset.id,
                network="TRON",
                destination_address="TTestWithdrawalDisabled123",
                amount=Decimal("5"),
                idempotency_key="phase43-withdrawal-disabled-test",
            )
        except ValueError as exc:
            if "Withdrawals are disabled" not in str(exc):
                raise AssertionError(
                    f"Unexpected error: {exc}"
                )
        else:
            raise AssertionError(
                "Expected withdrawal-disabled asset to be rejected"
            )

    finally:
        asset.withdrawal_enabled = original_value
        await db.rollback()

async def test_user_cannot_withdraw_from_another_users_account(db):
    print("\n[6] User cannot withdraw from another user's account")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    other_user_result = await db.execute(
        select(User).where(
            User.email != "user1@example.com"
        )
    )
    other_user = other_user_result.scalars().first()

    if other_user is None:
        raise AssertionError("No second user available for IDOR test")

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    other_account_result = await db.execute(
        select(Account).where(
            Account.user_id == other_user.id,
            Account.asset_id == asset.id,
            Account.account_type == "CUSTOMER",
        )
    )
    other_account = other_account_result.scalar_one_or_none()

    if other_account is None:
        raise AssertionError(
            "Second user's customer account does not exist"
        )

    try:
        await WithdrawalService.create_pending_withdrawal(
            db,
            user_id=user.id,
            asset_id=asset.id,
            network="TRON",
            destination_address="TTestIDORDestination123",
            amount=Decimal("5"),
            idempotency_key="phase43-withdrawal-idor-test",
        )
    except ValueError:
        # The service should use user1's own account.
        # A successful creation is also acceptable here because
        # it proves the supplied user_id controls account selection.
        pass

    withdrawal_result = await db.execute(
        select(Withdrawal).where(
            Withdrawal.user_id == user.id,
            Withdrawal.idempotency_key
            == "phase43-withdrawal-idor-test",
        )
    )
    withdrawal = withdrawal_result.scalar_one_or_none()

    if withdrawal is not None:
        if withdrawal.account_id == other_account.id:
            raise AssertionError(
                "IDOR vulnerability: withdrawal used another user's account"
            )

    await db.rollback()

async def test_ledger_failure_rolls_back_withdrawal_and_balance(db):
    print("\n[7] Ledger failure rolls back withdrawal and balance")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()
    user_id = user.id

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    customer_result = await db.execute(
        select(Account).where(
            Account.user_id == user.id,
            Account.asset_id == asset.id,
            Account.account_type == "CUSTOMER",
        )
    )
    customer = customer_result.scalar_one()

    customer_id = customer.id

    available_before = Decimal(
        str(customer.available_balance)
    )
    locked_before = Decimal(
        str(customer.locked_balance)
    )

    idempotency_key = "phase43-withdrawal-rollback-test"

    with patch(
        "app.services.withdrawal_service.LedgerService.create_transaction",
        new=AsyncMock(
            side_effect=RuntimeError("forced ledger failure")
        ),
    ):
        try:
            await WithdrawalService.create_pending_withdrawal(
                db,
                user_id=user.id,
                asset_id=asset.id,
                network="TRON",
                destination_address="TTestRollbackDestination123",
                amount=Decimal("5"),
                idempotency_key=idempotency_key,
            )
        except RuntimeError as exc:
            if str(exc) != "forced ledger failure":
                raise AssertionError(
                    f"Unexpected error: {exc}"
                )
        else:
            raise AssertionError(
                "Expected forced ledger failure"
            )

    await db.rollback()

    async with SessionLocal() as verify_db:
        customer_result = await verify_db.execute(
            select(Account).where(
                Account.id == customer_id
            )
        )
        customer_after = customer_result.scalar_one()

        if Decimal(
            str(customer_after.available_balance)
        ) != available_before:
            raise AssertionError(
                "Available balance changed after rollback"
            )

        if Decimal(
            str(customer_after.locked_balance)
        ) != locked_before:
            raise AssertionError(
                "Locked balance changed after rollback"
            )

        withdrawal_result = await verify_db.execute(
            select(Withdrawal).where(
                Withdrawal.user_id == user_id,
                Withdrawal.idempotency_key == idempotency_key,
            )
        )

        withdrawal = withdrawal_result.scalar_one_or_none()

        if withdrawal is not None:
            raise AssertionError(
                "Withdrawal persisted despite ledger failure"
            )

async def test_concurrent_withdrawals_cannot_overspend():
    print("\n[8] Concurrent withdrawals cannot overspend")

    async with SessionLocal() as setup_db:
        user_result = await setup_db.execute(
            select(User).where(
                User.email == "user1@example.com"
            )
        )
        user = user_result.scalar_one()

        asset_result = await setup_db.execute(
            select(Asset).where(
                Asset.symbol == "USDT"
            )
        )
        asset = asset_result.scalar_one()

        customer_result = await setup_db.execute(
            select(Account).where(
                Account.user_id == user.id,
                Account.asset_id == asset.id,
                Account.account_type == "CUSTOMER",
            )
        )
        customer = customer_result.scalar_one()

        customer_id = customer.id
        user_id = user.id
        asset_id = asset.id

        available_before = Decimal(
            str(customer.available_balance)
        )

        withdrawal_amount = (
            available_before / Decimal("2")
        ) + Decimal("0.000000001")

    async def attempt_withdrawal(idempotency_key):
        async with SessionLocal() as db:
            try:
                withdrawal = (
                    await WithdrawalService.create_pending_withdrawal(
                        db,
                        user_id=user_id,
                        asset_id=asset_id,
                        network="TRON",
                        destination_address=(
                            f"TConcurrent{ idempotency_key }"
                        ),
                        amount=withdrawal_amount,
                        idempotency_key=idempotency_key,
                    )
                )

                await db.commit()

                return ("success", withdrawal.id)

            except Exception as exc:
                await db.rollback()
                return ("failure", str(exc))

    result_1, result_2 = await asyncio.gather(
        attempt_withdrawal(
            "phase43-concurrent-withdrawal-1"
        ),
        attempt_withdrawal(
            "phase43-concurrent-withdrawal-2"
        ),
    )

    results = [result_1, result_2]

    successes = [
        result
        for result in results
        if result[0] == "success"
    ]

    failures = [
        result
        for result in results
        if result[0] == "failure"
    ]

    if len(successes) != 1:
        raise AssertionError(
            f"Expected exactly one successful withdrawal, "
            f"got {len(successes)}: {results}"
        )

    if len(failures) != 1:
        raise AssertionError(
            f"Expected exactly one failed withdrawal, "
            f"got {len(failures)}: {results}"
        )

    if "Insufficient available balance" not in failures[0][1]:
        raise AssertionError(
            f"Unexpected concurrency failure: {failures[0][1]}"
        )

    async with SessionLocal() as verify_db:
        customer_result = await verify_db.execute(
            select(Account).where(
                Account.id == customer_id
            )
        )
        customer_after = customer_result.scalar_one()

        available_after = Decimal(
            str(customer_after.available_balance)
        )
        locked_after = Decimal(
            str(customer_after.locked_balance)
        )

        if available_after != available_before - withdrawal_amount:
            raise AssertionError(
                "Concurrent withdrawals produced an "
                "incorrect available balance"
            )

        if locked_after != withdrawal_amount:
            raise AssertionError(
                "Expected the correct amount to be locked"
            )

        withdrawal_result = await verify_db.execute(
            select(Withdrawal).where(
                Withdrawal.user_id == user_id,
                Withdrawal.idempotency_key.in_(
                    [
                        "phase43-concurrent-withdrawal-1",
                        "phase43-concurrent-withdrawal-2",
                    ]
                ),
            )
        )

        withdrawals = list(
            withdrawal_result.scalars()
        )

        if len(withdrawals) != 1:
            raise AssertionError(
                f"Expected exactly one persisted withdrawal, "
                f"got {len(withdrawals)}"
            )

async def main():
    print("=" * 70)
    print("BITNOVA PHASE 4.3 WITHDRAWAL SERVICE TEST")
    print("=" * 70)

    async with SessionLocal() as db:
        await test_valid_withdrawal_creation(db)

    async with SessionLocal() as db:
        await test_withdrawal_is_idempotent(db)

    async with SessionLocal() as db:
        await test_idempotency_key_cannot_change_parameters(db)

    async with SessionLocal() as db:
        await test_insufficient_balance_does_not_lock_funds(db)

    async with SessionLocal() as db:
        await test_withdrawal_disabled_asset_is_rejected(db)

    async with SessionLocal() as db:
        await test_user_cannot_withdraw_from_another_users_account(db)

    async with SessionLocal() as db:
        await test_ledger_failure_rolls_back_withdrawal_and_balance(db)
        await test_concurrent_withdrawals_cannot_overspend()

    await engine.dispose()

    print("\n" + "=" * 70)
    print("PHASE 4.3 WITHDRAWAL INITIAL TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())