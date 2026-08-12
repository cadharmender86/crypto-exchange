import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
import asyncio
import uuid
from decimal import Decimal

import httpx
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from app.core.config import settings
from app.models.account import Account
from app.models.ledger_entry import LedgerEntry
from app.models.ledger_transaction import LedgerTransaction
from app.models.idempotency import IdempotencyRecord


BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

TOKEN = os.getenv("ACCESS_TOKEN")

SENDER_ID = uuid.UUID(
    "955767f7-fa07-4d10-ba04-75d8757b1e57"
)

RECEIVER_ID = uuid.UUID(
    "60df3023-8a8d-4910-98c7-b005fa1b744c"
)

USDT_ASSET_ID = uuid.UUID(
    "87e6d426-afc4-4bad-b2f5-7c48efe74246"
)


engine = create_async_engine(
    settings.database_url
)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


def auth_headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }


def unique_key(prefix):
    return (
        f"phase4.5-{prefix}-"
        f"{uuid.uuid4().hex}"
    )


async def get_account_balances():
    async with SessionLocal() as db:

        result = await db.execute(
            select(Account).where(
                Account.user_id.in_(
                    [SENDER_ID, RECEIVER_ID]
                ),
                Account.asset_id == USDT_ASSET_ID,
            )
        )

        accounts = result.scalars().all()

        balances = {}

        for account in accounts:
            balances[account.user_id] = {
                "available": Decimal(
                    str(account.available_balance)
                ),
                "locked": Decimal(
                    str(account.locked_balance)
                ),
                "total": (
                    Decimal(
                        str(account.available_balance)
                    )
                    +
                    Decimal(
                        str(account.locked_balance)
                    )
                ),
            }

        return balances


async def count_ledger_transactions():
    async with SessionLocal() as db:

        result = await db.execute(
            select(
                func.count(
                    LedgerTransaction.id
                )
            )
        )

        return result.scalar_one()


async def count_ledger_entries():
    async with SessionLocal() as db:

        result = await db.execute(
            select(
                func.count(
                    LedgerEntry.id
                )
            )
        )

        return result.scalar_one()


async def count_idempotency_records():
    async with SessionLocal() as db:

        result = await db.execute(
            select(
                func.count(
                    IdempotencyRecord.id
                )
            )
        )

        return result.scalar_one()


async def api_transfer(
    client,
    amount,
    key,
    to_user_id=None,
):
    payload = {
        "to_user_id": str(
            to_user_id or RECEIVER_ID
        ),
        "asset_id": str(
            USDT_ASSET_ID
        ),
        "amount": str(amount),
    }

    response = await client.post(
        "/api/v1/transfers",
        headers={
            **auth_headers(),
            "Idempotency-Key": key,
        },
        json=payload,
    )

    try:
        body = response.json()
    except Exception:
        body = response.text

    return response.status_code, body


async def test_insufficient_balance_rollback(
    client
):
    print("\n" + "=" * 70)
    print("[1] INSUFFICIENT BALANCE ROLLBACK")
    print("=" * 70)

    before = await get_account_balances()

    sender_before = before[SENDER_ID]
    receiver_before = before[RECEIVER_ID]

    print(
        "Sender before :",
        sender_before,
    )

    print(
        "Receiver before:",
        receiver_before,
    )

    status, body = await api_transfer(
        client,
        "999999999999",
        unique_key("insufficient"),
    )

    print(
        f"HTTP {status}: {body}"
    )

    if status != 400:
        raise AssertionError(
            f"Expected HTTP 400, got {status}"
        )

    after = await get_account_balances()

    sender_after = after[SENDER_ID]
    receiver_after = after[RECEIVER_ID]

    if sender_before != sender_after:
        raise AssertionError(
            "CRITICAL: sender balance changed "
            "after failed transfer"
        )

    if receiver_before != receiver_after:
        raise AssertionError(
            "CRITICAL: receiver balance changed "
            "after failed transfer"
        )

    print(
        "PASS - balances unchanged"
    )


async def test_invalid_destination_rollback(
    client
):
    print("\n" + "=" * 70)
    print("[2] INVALID DESTINATION ROLLBACK")
    print("=" * 70)

    before = await get_account_balances()

    fake_user = uuid.uuid4()

    status, body = await api_transfer(
        client,
        "1",
        unique_key("fake-destination"),
        fake_user,
    )

    print(
        f"HTTP {status}: {body}"
    )

    if status not in (400, 404):
        raise AssertionError(
            f"Expected HTTP 400/404, got {status}"
        )

    after = await get_account_balances()

    if before != after:
        raise AssertionError(
            "CRITICAL: balances changed after "
            "invalid destination"
        )

    print(
        "PASS - invalid destination rolled back"
    )


async def test_invalid_asset_rollback(
    client
):
    print("\n" + "=" * 70)
    print("[3] INVALID ASSET ROLLBACK")
    print("=" * 70)

    before = await get_account_balances()

    fake_asset = uuid.uuid4()

    payload = {
        "to_user_id": str(RECEIVER_ID),
        "asset_id": str(fake_asset),
        "amount": "1",
    }

    response = await client.post(
        "/api/v1/transfers",
        headers={
            **auth_headers(),
            "Idempotency-Key":
                unique_key("fake-asset"),
        },
        json=payload,
    )

    print(
        f"HTTP {response.status_code}: "
        f"{response.text}"
    )

    if response.status_code not in (400, 404):
        raise AssertionError(
            "Expected 400/404 for invalid asset"
        )

    after = await get_account_balances()

    if before != after:
        raise AssertionError(
            "CRITICAL: balances changed after "
            "invalid asset"
        )

    print(
        "PASS - invalid asset rolled back"
    )


async def test_failed_transfer_does_not_create_ledger(
    client
):
    print("\n" + "=" * 70)
    print("[4] FAILED TRANSFER MUST NOT CREATE LEDGER")
    print("=" * 70)

    transactions_before = (
        await count_ledger_transactions()
    )

    entries_before = (
        await count_ledger_entries()
    )

    status, body = await api_transfer(
        client,
        "-100",
        unique_key("negative"),
    )

    print(
        f"HTTP {status}: {body}"
    )

    if status not in (400, 422):
        raise AssertionError(
            f"Unexpected HTTP {status}"
        )

    transactions_after = (
        await count_ledger_transactions()
    )

    entries_after = (
        await count_ledger_entries()
    )

    print(
        f"Transactions before: {transactions_before}"
    )

    print(
        f"Transactions after : {transactions_after}"
    )

    print(
        f"Entries before     : {entries_before}"
    )

    print(
        f"Entries after      : {entries_after}"
    )

    if transactions_before != transactions_after:
        raise AssertionError(
            "CRITICAL: failed transfer created "
            "a ledger transaction"
        )

    if entries_before != entries_after:
        raise AssertionError(
            "CRITICAL: failed transfer created "
            "ledger entries"
        )

    print(
        "PASS - no ledger records created"
    )


async def test_failed_transfer_does_not_leave_idempotency(
    client
):
    print("\n" + "=" * 70)
    print("[5] FAILED TRANSFER IDEMPOTENCY STATE")
    print("=" * 70)

    key = unique_key("failed-idempotency")

    before = await count_idempotency_records()

    status, body = await api_transfer(
        client,
        "999999999999",
        key,
    )

    print(
        f"HTTP {status}: {body}"
    )

    if status != 400:
        raise AssertionError(
            f"Expected 400, got {status}"
        )

    after = await count_idempotency_records()

    print(
        f"Idempotency records before: "
        f"{before}"
    )

    print(
        f"Idempotency records after : "
        f"{after}"
    )

    if before != after:
        raise AssertionError(
            "Failed transaction left an "
            "idempotency record behind"
        )

    print(
        "PASS - failed transaction left "
        "no idempotency record"
    )


async def test_successful_transfer_atomicity(
    client
):
    print("\n" + "=" * 70)
    print("[6] SUCCESSFUL TRANSFER ATOMICITY")
    print("=" * 70)

    amount = Decimal("1")

    before = await get_account_balances()

    sender_before = before[SENDER_ID]
    receiver_before = before[RECEIVER_ID]

    key = unique_key("success")

    status, body = await api_transfer(
        client,
        amount,
        key,
    )

    print(
        f"HTTP {status}: {body}"
    )

    if status != 201:
        raise AssertionError(
            f"Expected 201, got {status}"
        )

    after = await get_account_balances()

    sender_after = after[SENDER_ID]
    receiver_after = after[RECEIVER_ID]

    sender_delta = (
        sender_before["available"]
        - sender_after["available"]
    )

    receiver_delta = (
        receiver_after["available"]
        - receiver_before["available"]
    )

    print(
        f"Sender delta  : {sender_delta}"
    )

    print(
        f"Receiver delta: {receiver_delta}"
    )

    if sender_delta != amount:
        raise AssertionError(
            "Sender balance delta is incorrect"
        )

    if receiver_delta != amount:
        raise AssertionError(
            "Receiver balance delta is incorrect"
        )

    if (
        sender_after["locked"] !=
        sender_before["locked"]
    ):
        raise AssertionError(
            "Sender locked balance changed"
        )

    if (
        receiver_after["locked"] !=
        receiver_before["locked"]
    ):
        raise AssertionError(
            "Receiver locked balance changed"
        )

    print(
        "PASS - successful transfer atomicity verified"
    )


async def test_replay_after_success(
    client
):
    print("\n" + "=" * 70)
    print("[7] REPLAY AFTER SUCCESS")
    print("=" * 70)

    key = unique_key("replay")

    first_status, first_body = (
        await api_transfer(
            client,
            "1",
            key,
        )
    )

    if first_status != 201:
        raise AssertionError(
            "Initial transfer failed"
        )

    transaction_id = (
        first_body["transaction_id"]
    )

    before_replay = (
        await get_account_balances()
    )

    second_status, second_body = (
        await api_transfer(
            client,
            "1",
            key,
        )
    )

    print(
        f"First : {first_status} {first_body}"
    )

    print(
        f"Replay: {second_status} {second_body}"
    )

    if second_status != 201:
        raise AssertionError(
            "Replay should return 201"
        )

    if (
        second_body["transaction_id"]
        != transaction_id
    ):
        raise AssertionError(
            "Replay created a different transaction"
        )

    after_replay = (
        await get_account_balances()
    )

    if before_replay != after_replay:
        raise AssertionError(
            "CRITICAL: idempotent replay changed "
            "account balances"
        )

    print(
        "PASS - replay caused no second balance change"
    )


async def main():

    print("=" * 70)
    print(
        "BITNOVA PHASE 4.5 "
        "TRANSACTION FAILURE / ROLLBACK TEST SUITE"
    )
    print("=" * 70)

    print(
        f"API: {BASE_URL}"
    )

    print(
        f"Sender: {SENDER_ID}"
    )

    print(
        f"Receiver: {RECEIVER_ID}"
    )

    print(
        f"Asset: USDT ({USDT_ASSET_ID})"
    )

    if not TOKEN:
        raise AssertionError(
            "ACCESS_TOKEN is not set"
        )

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=30,
    ) as client:

        await test_insufficient_balance_rollback(
            client
        )

        await test_invalid_destination_rollback(
            client
        )

        await test_invalid_asset_rollback(
            client
        )

        await test_failed_transfer_does_not_create_ledger(
            client
        )

        await test_failed_transfer_does_not_leave_idempotency(
            client
        )

        await test_successful_transfer_atomicity(
            client
        )

        await test_replay_after_success(
            client
        )

    await engine.dispose()

    print("\n" + "=" * 70)
    print("PHASE 4.5 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())