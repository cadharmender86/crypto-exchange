import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncio
import os
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from app.core.config import settings
from app.models.account import Account
from app.models.idempotency import IdempotencyRecord
from app.models.ledger_entry import LedgerEntry
from app.models.ledger_transaction import LedgerTransaction


# ============================================================
# CONFIG
# ============================================================

SENDER_ID = UUID(
    "955767f7-fa07-4d10-ba04-75d8757b1e57"
)

RECEIVER_ID = UUID(
    "60df3023-8a8d-4910-98c7-b005fa1b744c"
)

USDT_ASSET_ID = UUID(
    "87e6d426-afc4-4bad-b2f5-7c48efe74246"
)


engine = create_async_engine(
    settings.database_url
)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


# ============================================================
# HELPERS
# ============================================================

async def get_accounts(db):
    result = await db.execute(
        select(Account).where(
            Account.user_id.in_(
                [SENDER_ID, RECEIVER_ID]
            ),
            Account.asset_id == USDT_ASSET_ID,
        )
    )

    return result.scalars().all()


# ============================================================
# 1. NO NEGATIVE BALANCES
# ============================================================

async def test_no_negative_balances(db):
    print("\n[1] No negative account balances")

    result = await db.execute(
        select(Account).where(
            (Account.available_balance < 0)
            |
            (Account.locked_balance < 0)
        )
    )

    invalid_accounts = result.scalars().all()

    if invalid_accounts:
        for account in invalid_accounts:
            print(
                f"  INVALID ACCOUNT: {account.id} "
                f"available={account.available_balance} "
                f"locked={account.locked_balance}"
            )

        raise AssertionError(
            "CRITICAL: negative account balance detected"
        )

    print("  PASS")


# ============================================================
# 2. AVAILABLE + LOCKED BALANCE
# ============================================================

async def test_balance_components(db):
    print("\n[2] Account balance component integrity")

    accounts = await get_accounts(db)

    if not accounts:
        raise AssertionError(
            "No test accounts found"
        )

    for account in accounts:

        available = Decimal(
            str(account.available_balance)
        )

        locked = Decimal(
            str(account.locked_balance)
        )

        if available < 0:
            raise AssertionError(
                f"Negative available balance: "
                f"{account.id}"
            )

        if locked < 0:
            raise AssertionError(
                f"Negative locked balance: "
                f"{account.id}"
            )

        total = available + locked

        print(
            f"  {account.id}: "
            f"available={available}, "
            f"locked={locked}, "
            f"total={total}"
        )

    print("  PASS")


# ============================================================
# 3. EVERY LEDGER TRANSACTION HAS ENTRIES
# ============================================================

async def test_transactions_have_entries(db):
    print("\n[3] Every ledger transaction has entries")

    result = await db.execute(
        select(
            LedgerTransaction.id,
            func.count(
                LedgerEntry.id
            ).label("entry_count"),
        )
        .outerjoin(
            LedgerEntry,
            LedgerEntry.transaction_id
            == LedgerTransaction.id,
        )
        .group_by(
            LedgerTransaction.id
        )
        .having(
            func.count(
                LedgerEntry.id
            ) < 2
        )
    )

    invalid = result.all()

    if invalid:
        for transaction_id, count in invalid:
            print(
                f"  INVALID: {transaction_id} "
                f"entries={count}"
            )

        raise AssertionError(
            "CRITICAL: ledger transaction has "
            "fewer than two entries"
        )

    print("  PASS")


# ============================================================
# 4. EVERY TRANSFER IS BALANCED
# ============================================================

async def test_every_transaction_balanced(db):
    print("\n[4] Every ledger transaction is balanced")

    transactions_result = await db.execute(
        select(LedgerTransaction.id)
    )

    transaction_ids = (
        transactions_result.scalars().all()
    )

    checked = 0

    for transaction_id in transaction_ids:

        result = await db.execute(
            select(
                LedgerEntry.entry_type,
                func.coalesce(
                    func.sum(LedgerEntry.amount),
                    0,
                ),
            )
            .where(
                LedgerEntry.transaction_id
                == transaction_id
            )
            .group_by(
                LedgerEntry.entry_type
            )
        )

        rows = result.all()

        debit = Decimal("0")
        credit = Decimal("0")

        for entry_type, total in rows:

            total = Decimal(str(total))

            if entry_type == "DEBIT":
                debit += total

            elif entry_type == "CREDIT":
                credit += total

        if debit != credit:

            print(
                f"  INVALID TRANSACTION: "
                f"{transaction_id}"
            )

            print(
                f"    debit={debit}"
            )

            print(
                f"    credit={credit}"
            )

            raise AssertionError(
                "CRITICAL: unbalanced ledger transaction"
            )

        checked += 1

    print(
        f"  Checked transactions: {checked}"
    )

    print("  PASS")


# ============================================================
# 5. NO ORPHAN LEDGER ENTRIES
# ============================================================

async def test_no_orphan_ledger_entries(db):
    print("\n[5] No orphan ledger entries")

    result = await db.execute(
        select(LedgerEntry.id)
        .outerjoin(
            LedgerTransaction,
            LedgerTransaction.id
            == LedgerEntry.transaction_id,
        )
        .where(
            LedgerTransaction.id.is_(None)
        )
    )

    orphan_entries = result.scalars().all()

    if orphan_entries:
        print(
            f"  Orphan entries: "
            f"{len(orphan_entries)}"
        )

        raise AssertionError(
            "CRITICAL: orphan ledger entries found"
        )

    print("  PASS")


# ============================================================
# 6. NO LEDGER ENTRY WITHOUT ACCOUNT
# ============================================================

async def test_no_orphan_account_entries(db):
    print("\n[6] No ledger entries referencing "
          "missing accounts")

    result = await db.execute(
        select(LedgerEntry.id)
        .outerjoin(
            Account,
            Account.id
            == LedgerEntry.account_id,
        )
        .where(
            Account.id.is_(None)
        )
    )

    orphan_entries = result.scalars().all()

    if orphan_entries:

        print(
            f"  Invalid entries: "
            f"{len(orphan_entries)}"
        )

        raise AssertionError(
            "CRITICAL: ledger entry references "
            "non-existent account"
        )

    print("  PASS")


# ============================================================
# 7. NO DUPLICATE IDEMPOTENCY KEYS
# ============================================================

async def test_no_duplicate_idempotency_keys(db):
    print("\n[7] No duplicate idempotency keys")

    result = await db.execute(
        select(
            IdempotencyRecord.user_id,
            IdempotencyRecord.idempotency_key,
            func.count(
                IdempotencyRecord.id
            ).label("count"),
        )
        .group_by(
            IdempotencyRecord.user_id,
            IdempotencyRecord.idempotency_key,
        )
        .having(
            func.count(
                IdempotencyRecord.id
            ) > 1
        )
    )

    duplicates = result.all()

    if duplicates:

        for user_id, key, count in duplicates:

            print(
                f"  DUPLICATE: user={user_id} "
                f"key={key} count={count}"
            )

        raise AssertionError(
            "CRITICAL: duplicate idempotency records found"
        )

    print("  PASS")


# ============================================================
# 8. COMPLETED IDEMPOTENCY RECORDS HAVE TRANSACTIONS
# ============================================================

async def test_completed_idempotency_integrity(db):
    print(
        "\n[8] Completed idempotency records "
        "reference valid transactions"
    )

    result = await db.execute(
        select(IdempotencyRecord)
        .where(
            IdempotencyRecord.status == "COMPLETED"
        )
    )

    records = result.scalars().all()

    checked = 0

    for record in records:

        if record.transaction_id is None:

            raise AssertionError(
                "CRITICAL: COMPLETED idempotency "
                f"record {record.id} has no transaction"
            )

        transaction_result = await db.execute(
            select(LedgerTransaction).where(
                LedgerTransaction.id
                == record.transaction_id
            )
        )

        transaction = (
            transaction_result.scalar_one_or_none()
        )

        if transaction is None:

            raise AssertionError(
                "CRITICAL: idempotency record "
                f"{record.id} references "
                "non-existent transaction"
            )

        checked += 1

    print(
        f"  Checked completed records: {checked}"
    )

    print("  PASS")


# ============================================================
# 9. TRANSACTION STATUS INTEGRITY
# ============================================================

async def test_transaction_status(db):
    print("\n[9] Transaction status integrity")

    result = await db.execute(
        select(LedgerTransaction)
    )

    transactions = result.scalars().all()

    allowed_statuses = {
        "POSTED",
        "COMPLETED",
        "FAILED",
        "PENDING",
    }

    for transaction in transactions:

        if transaction.status not in allowed_statuses:

            raise AssertionError(
                f"Invalid transaction status "
                f"{transaction.status} "
                f"for {transaction.id}"
            )

    print(
        f"  Checked transactions: "
        f"{len(transactions)}"
    )

    print("  PASS")


# ============================================================
# 10. GLOBAL DEBIT / CREDIT BALANCE
# ============================================================

async def test_global_ledger_balance(db):
    print("\n[10] Global ledger debit/credit balance")

    debit_result = await db.execute(
        select(
            func.coalesce(
                func.sum(LedgerEntry.amount),
                0,
            )
        ).where(
            LedgerEntry.entry_type == "DEBIT"
        )
    )

    credit_result = await db.execute(
        select(
            func.coalesce(
                func.sum(LedgerEntry.amount),
                0,
            )
        ).where(
            LedgerEntry.entry_type == "CREDIT"
        )
    )

    debit = Decimal(
        str(debit_result.scalar_one())
    )

    credit = Decimal(
        str(credit_result.scalar_one())
    )

    print(
        f"  Total debit : {debit}"
    )

    print(
        f"  Total credit: {credit}"
    )

    if debit != credit:

        raise AssertionError(
            "CRITICAL: global ledger is unbalanced"
        )

    print("  PASS")


# ============================================================
# 11. TEST USER LEDGER RECONCILIATION
# ============================================================

async def reconcile_account(
    db,
    account,
):
    debit_result = await db.execute(
        select(
            func.coalesce(
                func.sum(LedgerEntry.amount),
                0,
            )
        ).where(
            LedgerEntry.account_id == account.id,
            LedgerEntry.entry_type == "DEBIT",
        )
    )

    credit_result = await db.execute(
        select(
            func.coalesce(
                func.sum(LedgerEntry.amount),
                0,
            )
        ).where(
            LedgerEntry.account_id == account.id,
            LedgerEntry.entry_type == "CREDIT",
        )
    )

    debit = Decimal(
        str(debit_result.scalar_one())
    )

    credit = Decimal(
        str(credit_result.scalar_one())
    )

    ledger_net = credit - debit

    available = Decimal(
        str(account.available_balance)
    )

    locked = Decimal(
        str(account.locked_balance)
    )

    account_total = (
        available + locked
    )

    return (
        debit,
        credit,
        ledger_net,
        account_total,
    )


async def test_account_ledger_reconciliation(db):
    print(
        "\n[11] Account ↔ ledger reconciliation"
    )

    accounts = await get_accounts(db)

    for account in accounts:

        (
            debit,
            credit,
            ledger_net,
            account_total,
        ) = await reconcile_account(
            db,
            account,
        )

        print(
            f"\n  Account: {account.id}"
        )

        print(
            f"    Debit      : {debit}"
        )

        print(
            f"    Credit     : {credit}"
        )

        print(
            f"    Ledger net : {ledger_net}"
        )

        print(
            f"    Account    : {account_total}"
        )

        # This comparison assumes the account's ledger
        # represents the complete balance history.
        if ledger_net != account_total:

            raise AssertionError(
                f"Account/ledger mismatch for "
                f"{account.id}: "
                f"ledger={ledger_net}, "
                f"account={account_total}"
            )

    print("\n  PASS")


# ============================================================
# 12. FINAL INTEGRITY SUMMARY
# ============================================================

async def final_summary(db):

    print("\n" + "=" * 70)
    print("FINAL DATABASE INTEGRITY SUMMARY")
    print("=" * 70)

    transaction_count = (
        await db.scalar(
            select(
                func.count(
                    LedgerTransaction.id
                )
            )
        )
    )

    entry_count = (
        await db.scalar(
            select(
                func.count(
                    LedgerEntry.id
                )
            )
        )
    )

    idempotency_count = (
        await db.scalar(
            select(
                func.count(
                    IdempotencyRecord.id
                )
            )
        )
    )

    account_count = (
        await db.scalar(
            select(
                func.count(
                    Account.id
                )
            )
        )

    )

    print(
        f"Ledger transactions : {transaction_count}"
    )

    print(
        f"Ledger entries      : {entry_count}"
    )

    print(
        f"Idempotency records : {idempotency_count}"
    )

    print(
        f"Accounts            : {account_count}"
    )

    print("\nALL DATABASE INTEGRITY CHECKS PASSED")


# ============================================================
# MAIN
# ============================================================

async def main():

    print("=" * 70)
    print("BITNOVA PHASE 4.6 DATABASE / LEDGER INTEGRITY TEST")
    print("=" * 70)

    print(
        f"Sender  : {SENDER_ID}"
    )

    print(
        f"Receiver: {RECEIVER_ID}"
    )

    print(
        f"USDT    : {USDT_ASSET_ID}"
    )

    async with SessionLocal() as db:

        await test_no_negative_balances(db)

        await test_balance_components(db)

        await test_transactions_have_entries(db)

        await test_every_transaction_balanced(db)

        await test_no_orphan_ledger_entries(db)

        await test_no_orphan_account_entries(db)

        await test_no_duplicate_idempotency_keys(db)

        await test_completed_idempotency_integrity(db)

        await test_transaction_status(db)

        await test_global_ledger_balance(db)

        await test_account_ledger_reconciliation(db)

        await final_summary(db)

    await engine.dispose()

    print("\n" + "=" * 70)
    print("PHASE 4.6 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())