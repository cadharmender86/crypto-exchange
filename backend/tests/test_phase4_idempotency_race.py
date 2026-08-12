import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
import asyncio
import uuid
from decimal import Decimal

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.idempotency import IdempotencyRecord
from app.models.ledger_entry import LedgerEntry
from app.models.ledger_transaction import LedgerTransaction


BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

TOKEN = os.getenv("ACCESS_TOKEN")

SENDER_ID = "955767f7-fa07-4d10-ba04-75d8757b1e57"
RECEIVER_ID = "60df3023-8a8d-4910-98c7-b005fa1b744c"

USDT_ASSET_ID = "87e6d426-afc4-4bad-b2f5-7c48efe74246"


engine = create_async_engine(settings.database_url)
SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


def headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }


def unique_key(prefix):
    return f"phase4.4-{prefix}-{uuid.uuid4().hex}"


async def make_transfer(
    client,
    request_name,
    idempotency_key,
    amount="1",
):
    payload = {
        "to_user_id": RECEIVER_ID,
        "asset_id": USDT_ASSET_ID,
        "amount": amount,
    }

    print(
        f"[{request_name}] Sending request "
        f"Idempotency-Key={idempotency_key}"
    )

    response = await client.post(
        "/api/v1/transfers",
        headers={
            **headers(),
            "Idempotency-Key": idempotency_key,
        },
        json=payload,
    )

    try:
        body = response.json()
    except Exception:
        body = response.text

    print(
        f"[{request_name}] "
        f"HTTP {response.status_code}: {body}"
    )

    return response.status_code, body


async def get_sender_balance(client):
    response = await client.get(
        "/api/v1/accounts",
        headers=headers(),
    )

    if response.status_code != 200:
        raise AssertionError(
            f"Unable to retrieve sender account: "
            f"HTTP {response.status_code}"
        )

    accounts = response.json()

    for account in accounts:
        if account["asset_id"] == USDT_ASSET_ID:
            return Decimal(
                str(account["available_balance"])
            )

    raise AssertionError(
        "Sender USDT account was not found"
    )


async def test_same_key_concurrent_requests(client):
    print("\n" + "=" * 70)
    print("[1] SAME IDEMPOTENCY KEY — 10 CONCURRENT REQUESTS")
    print("=" * 70)

    idempotency_key = unique_key("same-key")

    amount = "1"

    before_balance = await get_sender_balance(client)

    print(f"Balance before: {before_balance}")

    tasks = []

    for i in range(10):
        tasks.append(
            make_transfer(
                client,
                f"REQUEST-{i + 1}",
                idempotency_key,
                amount,
            )
        )

    results = await asyncio.gather(*tasks)

    status_codes = [result[0] for result in results]

    successful = [
        result
        for result in results
        if result[0] == 201
    ]

    print("\nResult summary:")
    print(f"  Total requests : {len(results)}")
    print(f"  HTTP 201       : {status_codes.count(201)}")
    print(f"  HTTP 400       : {status_codes.count(400)}")
    print(f"  HTTP 409       : {status_codes.count(409)}")
    print(f"  Other          : {len(results) - status_codes.count(201) - status_codes.count(400) - status_codes.count(409)}")

    if not successful:
        raise AssertionError(
            "No request succeeded"
        )

    # All successful/replayed responses should identify
    # the same transaction.
    transaction_ids = set()

    for status, body in successful:
        if isinstance(body, dict):
            transaction_id = body.get("transaction_id")

            if transaction_id:
                transaction_ids.add(
                    transaction_id
                )

    print(
        f"  Unique transaction IDs: "
        f"{len(transaction_ids)}"
    )

    if len(transaction_ids) != 1:
        raise AssertionError(
            "CRITICAL: same idempotency key produced "
            f"{len(transaction_ids)} different transactions"
        )

    after_balance = await get_sender_balance(client)

    print(f"Balance after : {after_balance}")

    balance_change = before_balance - after_balance

    print(f"Balance change: {balance_change}")

    if balance_change != Decimal(amount):
        raise AssertionError(
            "CRITICAL: balance changed by something other "
            f"than exactly {amount}"
        )

    print("PASS - same idempotency key executed only once")

    return idempotency_key, next(iter(transaction_ids))


async def test_same_key_replay(client):
    print("\n" + "=" * 70)
    print("[2] IDEMPOTENCY REPLAY")
    print("=" * 70)

    idempotency_key = unique_key("replay")

    payload = {
        "to_user_id": RECEIVER_ID,
        "asset_id": USDT_ASSET_ID,
        "amount": "1",
    }

    first = await client.post(
        "/api/v1/transfers",
        headers={
            **headers(),
            "Idempotency-Key": idempotency_key,
        },
        json=payload,
    )

    print(
        f"First request: "
        f"HTTP {first.status_code}: "
        f"{first.text}"
    )

    if first.status_code != 201:
        raise AssertionError(
            f"First request failed: "
            f"{first.status_code}"
        )

    first_body = first.json()

    second = await client.post(
        "/api/v1/transfers",
        headers={
            **headers(),
            "Idempotency-Key": idempotency_key,
        },
        json=payload,
    )

    print(
        f"Replay request: "
        f"HTTP {second.status_code}: "
        f"{second.text}"
    )

    if second.status_code != 201:
        raise AssertionError(
            "Idempotent replay should return "
            "the original successful response"
        )

    second_body = second.json()

    if (
        first_body.get("transaction_id")
        != second_body.get("transaction_id")
    ):
        raise AssertionError(
            "Replay returned a different transaction"
        )

    if (
        first_body.get("reference")
        != second_body.get("reference")
    ):
        raise AssertionError(
            "Replay returned a different reference"
        )

    print("PASS - replay returned original transaction")


async def test_same_key_different_request(client):
    print("\n" + "=" * 70)
    print("[3] SAME KEY + DIFFERENT REQUEST")
    print("=" * 70)

    idempotency_key = unique_key("mismatch")

    first_payload = {
        "to_user_id": RECEIVER_ID,
        "asset_id": USDT_ASSET_ID,
        "amount": "1",
    }

    second_payload = {
        "to_user_id": RECEIVER_ID,
        "asset_id": USDT_ASSET_ID,
        "amount": "2",
    }

    first = await client.post(
        "/api/v1/transfers",
        headers={
            **headers(),
            "Idempotency-Key": idempotency_key,
        },
        json=first_payload,
    )

    print(
        f"First: "
        f"HTTP {first.status_code}: "
        f"{first.text}"
    )

    if first.status_code != 201:
        raise AssertionError(
            "Initial request failed"
        )

    second = await client.post(
        "/api/v1/transfers",
        headers={
            **headers(),
            "Idempotency-Key": idempotency_key,
        },
        json=second_payload,
    )

    print(
        f"Different request: "
        f"HTTP {second.status_code}: "
        f"{second.text}"
    )

    if second.status_code != 400:
        raise AssertionError(
            "Same idempotency key with different "
            f"request should return 400, "
            f"received {second.status_code}"
        )

    print(
        "PASS - request mismatch rejected"
    )


async def test_different_keys_concurrent(client):
    print("\n" + "=" * 70)
    print("[4] DIFFERENT KEYS — CONCURRENT TRANSFERS")
    print("=" * 70)

    amount = "1"

    before_balance = await get_sender_balance(client)

    print(f"Balance before: {before_balance}")

    number_of_requests = 5

    tasks = []

    for i in range(number_of_requests):
        tasks.append(
            make_transfer(
                client,
                f"DIFFERENT-KEY-{i + 1}",
                unique_key(f"different-{i + 1}"),
                amount,
            )
        )

    results = await asyncio.gather(*tasks)

    successful = [
        result
        for result in results
        if result[0] == 201
    ]

    failed = [
        result
        for result in results
        if result[0] != 201
    ]

    print("\nResult summary:")
    print(f"  Total     : {len(results)}")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed    : {len(failed)}")

    after_balance = await get_sender_balance(client)

    print(f"Balance after: {after_balance}")

    balance_change = before_balance - after_balance

    expected_change = Decimal(
        str(len(successful))
    ) * Decimal(amount)

    print(
        f"Balance change : {balance_change}"
    )

    print(
        f"Expected change: {expected_change}"
    )

    if balance_change != expected_change:
        raise AssertionError(
            "Balance change does not match "
            "successful transfers"
        )

    if after_balance < Decimal("0"):
        raise AssertionError(
            "CRITICAL: account balance became negative"
        )

    print(
        "PASS - concurrent transfers remained "
        "financially consistent"
    )


async def verify_database_integrity(
    transaction_id=None,
    idempotency_key=None,
):
    print("\n" + "=" * 70)
    print("[5] DATABASE INTEGRITY VERIFICATION")
    print("=" * 70)

    async with SessionLocal() as session:

        if transaction_id:

            transaction_result = await session.execute(
                select(
                    LedgerTransaction
                ).where(
                    LedgerTransaction.id
                    == uuid.UUID(transaction_id)
                )
            )

            transaction = (
                transaction_result.scalar_one_or_none()
            )

            if transaction is None:
                raise AssertionError(
                    "Expected transaction was not found"
                )

            print(
                f"Transaction: {transaction.id}"
            )

            entry_result = await session.execute(
                select(
                    LedgerEntry
                ).where(
                    LedgerEntry.transaction_id
                    == transaction.id
                )
            )

            entries = entry_result.scalars().all()

            print(
                f"Ledger entries: {len(entries)}"
            )

            if len(entries) != 2:
                raise AssertionError(
                    "Transfer should contain exactly "
                    "2 ledger entries"
                )

            debit_total = sum(
                (
                    Decimal(str(entry.amount))
                    for entry in entries
                    if entry.entry_type == "DEBIT"
                ),
                Decimal("0"),
            )

            credit_total = sum(
                (
                    Decimal(str(entry.amount))
                    for entry in entries
                    if entry.entry_type == "CREDIT"
                ),
                Decimal("0"),
            )

            print(
                f"Debit : {debit_total}"
            )

            print(
                f"Credit: {credit_total}"
            )

            if debit_total != credit_total:
                raise AssertionError(
                    "CRITICAL: ledger debit != credit"
                )

            print(
                "PASS - ledger transaction balanced"
            )

        if idempotency_key:

            result = await session.execute(
                select(
                    func.count(
                        IdempotencyRecord.id
                    )
                ).where(
                    IdempotencyRecord.idempotency_key
                    == idempotency_key
                )
            )

            count = result.scalar_one()

            print(
                f"Idempotency records for key: "
                f"{count}"
            )

            if count != 1:
                raise AssertionError(
                    "Expected exactly one idempotency "
                    f"record, found {count}"
                )

            print(
                "PASS - exactly one idempotency record"
            )


async def main():

    print("=" * 70)
    print("BITNOVA PHASE 4.4 IDEMPOTENCY / RACE-CONDITION TEST SUITE")
    print("=" * 70)

    print(f"API: {BASE_URL}")
    print(f"Sender: {SENDER_ID}")
    print(f"Receiver: {RECEIVER_ID}")
    print(f"Asset: USDT ({USDT_ASSET_ID})")

    if not TOKEN:
        raise AssertionError(
            "ACCESS_TOKEN environment variable is not set"
        )

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=30,
    ) as client:

        same_key, transaction_id = (
            await test_same_key_concurrent_requests(
                client
            )
        )

        await verify_database_integrity(
            transaction_id=transaction_id,
            idempotency_key=same_key,
        )

        await test_same_key_replay(client)

        await test_same_key_different_request(
            client
        )

        await test_different_keys_concurrent(
            client
        )

    await engine.dispose()

    print("\n" + "=" * 70)
    print("PHASE 4.4 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())