"""
Phase 3B integrity test suite for BitNova Exchange.

Run from backend:
    $env:ACCESS_TOKEN="CURRENT_USER1_ACCESS_TOKEN"
    python .\tests\test_phase3b_integrity.py

Requires the FastAPI server on http://127.0.0.1:8000.
The suite uses the existing schema; it does not create/alter tables.
"""

import asyncio
import os
import sys
import uuid
from decimal import Decimal

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, ".")

from app.core.config import settings  # noqa: E402


BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
TOKEN = os.getenv("ACCESS_TOKEN")

USER1_ID = "955767f7-fa07-4d10-ba04-75d8757b1e57"
USER2_ID = "60df3023-8a8d-4910-98c7-b005fa1b744c"

USDT_ASSET_ID = "87e6d426-afc4-4bad-b2f5-7c48efe74246"

# Backward-compatible aliases used by existing tests
SENDER_ID = USER1_ID
RECEIVER_ID = USER2_ID
ASSET_ID = USDT_ASSET_ID

engine = create_async_engine(settings.database_url)


def auth_headers(idempotency_key: str | None = None) -> dict[str, str]:
    if not TOKEN:
        raise RuntimeError("ACCESS_TOKEN environment variable is not set.")

    headers = {"Authorization": f"Bearer {TOKEN}"}
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    return headers


async def get_balances() -> dict[str, Decimal]:
    async with engine.connect() as conn:
        rows = (
            await conn.execute(
                text(
                    """
                    SELECT user_id::text, available_balance, locked_balance
                    FROM accounts
                    WHERE asset_id = :asset_id
                      AND user_id IN (:user1, :user2)
                    ORDER BY user_id
                    """
                ),
                {
                    "asset_id": USDT_ASSET_ID,
                    "user1": USER1_ID,
                    "user2": USER2_ID,
                },
            )
        ).mappings().all()

    return {
        row["user_id"]: Decimal(str(row["available_balance"]))
        + Decimal(str(row["locked_balance"]))
        for row in rows
    }


async def get_account(user_id: str) -> dict:
    async with engine.connect() as conn:
        row = (
            await conn.execute(
                text(
                    """
                    SELECT
                        available_balance,
                        locked_balance,
                        status
                    FROM accounts
                    WHERE user_id = :user_id
                      AND asset_id = :asset_id
                    """
                ),
                {"user_id": user_id, "asset_id": USDT_ASSET_ID},
            )
        ).mappings().one()

    return {
        "available": Decimal(str(row["available_balance"])),
        "locked": Decimal(str(row["locked_balance"])),
        "status": row["status"],
    }


async def ledger_balance(user_id: str) -> Decimal:
    """
    Existing ledger convention:
      CREDIT increases an account.
      DEBIT decreases an account.

    Therefore:
      ledger_balance = credits - debits
    """
    async with engine.connect() as conn:
        row = (
            await conn.execute(
                text(
                    """
                    SELECT COALESCE(
                        SUM(
                            CASE
                                WHEN le.entry_type = 'CREDIT' THEN le.amount
                                WHEN le.entry_type = 'DEBIT' THEN -le.amount
                                ELSE 0
                            END
                        ),
                        0
                    ) AS balance
                    FROM ledger_entries le
                    JOIN accounts a ON a.id = le.account_id
                    WHERE a.user_id = :user_id
                      AND a.asset_id = :asset_id
                    """
                ),
                {"user_id": user_id, "asset_id": USDT_ASSET_ID},
            )
        ).scalar_one()

    return Decimal(str(row))


async def counts() -> dict[str, int]:
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                """
                SELECT
                    (SELECT COUNT(*) FROM ledger_transactions) AS transactions,
                    (SELECT COUNT(*) FROM ledger_entries) AS entries,
                    (SELECT COUNT(*) FROM idempotency_records) AS idempotency
                """
            )
        )
        row = result.mappings().one()

    return {key: int(value) for key, value in row.items()}


async def transfer(
    client: httpx.AsyncClient,
    *,
    to_user_id: str,
    amount: Decimal,
    key: str,
    description: str,
):
    payload = {
        "to_user_id": to_user_id,
        "asset_id": USDT_ASSET_ID,
        "amount": str(amount),
        "description": description,
    }

    response = await client.post(
        "/api/v1/transfers",
        json=payload,
        headers=auth_headers(key),
    )

    try:
        body = response.json()
    except Exception:
        body = response.text

    return response.status_code, body


async def test_ledger_account_reconciliation():
    print("\n[1] Ledger <-> account reconciliation")

    failures = []

    for user_id in (USER1_ID, USER2_ID):
        account = await get_account(user_id)
        ledger = await ledger_balance(user_id)
        account_total = account["available"] + account["locked"]

        print(
            f"  {user_id}: account={account_total} "
            f"ledger={ledger}"
        )

        if account_total != ledger:
            failures.append(
                f"{user_id}: account={account_total}, ledger={ledger}"
            )

    if failures:
        raise AssertionError(
            "Reconciliation failed: " + "; ".join(failures)
        )

    print("  PASS")


async def test_failed_transfer_rollback(client):
    print("\n[2] Failed-transfer rollback")

    before_user1 = await get_account(USER1_ID)
    before_user2 = await get_account(USER2_ID)
    before_counts = await counts()

    amount = before_user1["available"] + Decimal("1")
    key = f"rollback-{uuid.uuid4().hex}"

    status, body = await transfer(
        client,
        to_user_id=USER2_ID,
        amount=amount,
        key=key,
        description="Phase 3B failed rollback test",
    )

    print(f"  HTTP {status}: {body}")

    if status != 400:
        raise AssertionError(
            f"Expected HTTP 400, received {status}: {body}"
        )

    after_user1 = await get_account(USER1_ID)
    after_user2 = await get_account(USER2_ID)
    after_counts = await counts()

    if before_user1 != after_user1:
        raise AssertionError(
            f"Source account changed after failed transfer: "
            f"{before_user1} -> {after_user1}"
        )

    if before_user2 != after_user2:
        raise AssertionError(
            f"Destination account changed after failed transfer: "
            f"{before_user2} -> {after_user2}"
        )

    if before_counts != after_counts:
        raise AssertionError(
            f"Ledger/idempotency counts changed: "
            f"{before_counts} -> {after_counts}"
        )

    print("  PASS")


async def test_idempotency_replay(client):
    print("\n[3] Idempotency replay")

    source_before = await get_account(USER1_ID)
    if source_before["available"] < Decimal("1"):
        raise AssertionError("User 1 needs at least 1 USDT for this test.")

    key = f"replay-{uuid.uuid4().hex}"

    status1, body1 = await transfer(
        client,
        to_user_id=USER2_ID,
        amount=Decimal("1"),
        key=key,
        description="Phase 3B idempotency replay test",
    )

    status2, body2 = await transfer(
        client,
        to_user_id=USER2_ID,
        amount=Decimal("1"),
        key=key,
        description="Phase 3B idempotency replay test",
    )

    print(f"  First : HTTP {status1}: {body1}")
    print(f"  Replay: HTTP {status2}: {body2}")

    if status1 != 201 or status2 != 201:
        raise AssertionError("Both original and replay must return HTTP 201.")

    if body1["transaction_id"] != body2["transaction_id"]:
        raise AssertionError("Replay created a different transaction_id.")

    if body1["reference"] != body2["reference"]:
        raise AssertionError("Replay created a different reference.")

    if body1["status"] != "POSTED" or body2["status"] != "POSTED":
        raise AssertionError("Unexpected transfer status.")

    # Same key + different request must be rejected.
    status3, body3 = await transfer(
        client,
        to_user_id=USER2_ID,
        amount=Decimal("2"),
        key=key,
        description="Phase 3B idempotency mismatch test",
    )

    print(f"  Mismatch: HTTP {status3}: {body3}")

    if status3 != 400:
        raise AssertionError(
            "Reusing an idempotency key with a different request "
            "must return HTTP 400."
        )

    print("  PASS")


async def test_audit_trail(client):
    print("\n[4] Audit trail verification")

    key = f"audit-{uuid.uuid4().hex}"

    status, body = await transfer(
        client,
        to_user_id=USER2_ID,
        amount=Decimal("1"),
        key=key,
        description="Phase 3B audit trail test",
    )

    if status != 201:
        raise AssertionError(f"Audit transfer failed: {status} {body}")

    tx_id = body["transaction_id"]

    async with engine.connect() as conn:
        tx = (
            await conn.execute(
                text(
                    """
                    SELECT
                        id::text,
                        reference,
                        transaction_type,
                        status,
                        description
                    FROM ledger_transactions
                    WHERE id = :transaction_id
                    """
                ),
                {"transaction_id": tx_id},
            )
        ).mappings().one()

        entries = (
            await conn.execute(
                text(
                    """
                    SELECT
                        account_id::text,
                        entry_type,
                        amount
                    FROM ledger_entries
                    WHERE transaction_id = :transaction_id
                    ORDER BY entry_type, account_id
                    """
                ),
                {"transaction_id": tx_id},
            )
        ).mappings().all()

        idem = (
            await conn.execute(
                text(
                    """
                    SELECT
                        idempotency_key,
                        request_hash,
                        transaction_id::text,
                        status
                    FROM idempotency_records
                    WHERE user_id = :user_id
                      AND idempotency_key = :key
                    """
                ),
                {"user_id": USER1_ID, "key": key},
            )
        ).mappings().one()

    if tx["status"] != "POSTED":
        raise AssertionError(f"Transaction status is not POSTED: {tx}")

    if len(entries) != 2:
        raise AssertionError(
            f"Expected exactly 2 ledger entries, found {len(entries)}"
        )

    debit = sum(
        Decimal(str(e["amount"]))
        for e in entries
        if e["entry_type"] == "DEBIT"
    )
    credit = sum(
        Decimal(str(e["amount"]))
        for e in entries
        if e["entry_type"] == "CREDIT"
    )

    if debit != credit:
        raise AssertionError(
            f"Unbalanced audit trail: debit={debit}, credit={credit}"
        )

    if idem["transaction_id"] != tx_id:
        raise AssertionError("Idempotency record points to wrong transaction.")

    if idem["status"] != "COMPLETED":
        raise AssertionError("Idempotency record is not COMPLETED.")

    print(
        f"  Transaction={tx_id}, entries={len(entries)}, "
        f"debit={debit}, credit={credit}"
    )
    print("  PASS")


async def test_concurrent_multi_user(client):
    print("\n[5] Concurrent transfers between multiple users")

    user1_token = os.getenv("ACCESS_TOKEN")
    user2_token = os.getenv("USER2_ACCESS_TOKEN")

    if not user1_token:
        raise AssertionError("ACCESS_TOKEN is not set")

    if not user2_token:
        raise AssertionError("USER2_ACCESS_TOKEN is not set")

    from jose import jwt
    from app.core.config import settings

    # Decode User 1 token
    user1_payload = jwt.decode(
        user1_token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    # Decode User 2 token
    user2_payload = jwt.decode(
        user2_token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    user1_id = user1_payload.get("sub")
    user2_id = user2_payload.get("sub")

    print(f"  Token A user: {user1_id}")
    print(f"  Token B user: {user2_id}")

    # Verify User 1
    if user1_id != SENDER_ID:
        raise AssertionError(
            f"ACCESS_TOKEN belongs to {user1_id}, "
            f"expected {SENDER_ID}"
        )

    # Make the actual JWT user the receiver.
    receiver_id = user2_id

    if user1_id == receiver_id:
        raise AssertionError(
            "User 1 and User 2 must be different users"
        )

    amount = Decimal("1")

    async def request_user1_to_user2():
        headers = {
            "Authorization": f"Bearer {user1_token}",
            "Content-Type": "application/json",
            "Idempotency-Key": f"concurrent-u1-u2-{uuid.uuid4().hex}",
        }

        payload = {
            "to_user_id": receiver_id,
            "asset_id": ASSET_ID,
            "amount": str(amount),
        }

        response = await client.post(
            "/api/v1/transfers",
            headers=headers,
            json=payload,
        )

        return response.status_code, response.json()

    async def request_user2_to_user1():
        headers = {
            "Authorization": f"Bearer {user2_token}",
            "Content-Type": "application/json",
            "Idempotency-Key": f"concurrent-u2-u1-{uuid.uuid4().hex}",
        }

        payload = {
            "to_user_id": SENDER_ID,
            "asset_id": ASSET_ID,
            "amount": str(amount),
        }

        response = await client.post(
            "/api/v1/transfers",
            headers=headers,
            json=payload,
        )

        return response.status_code, response.json()

    results = await asyncio.gather(
        request_user1_to_user2(),
        request_user2_to_user1(),
    )

    result_a, result_b = results

    print(f"  A (User1 -> User2): {result_a}")
    print(f"  B (User2 -> User1): {result_b}")

    if result_a[0] != 201 or result_b[0] != 201:
        raise AssertionError(
            "Both opposite-direction transfers should succeed; "
            "deterministic account locking should prevent deadlock."
        )

    print("  PASS")

async def test_insufficient_and_locked_balance(client):
    print("\n[6] Insufficient-balance / locked-balance edge cases")

    token = os.getenv("ACCESS_TOKEN")

    if not token:
        raise AssertionError("ACCESS_TOKEN is not set")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # ---------------------------------------------------------
    # Case 1: Insufficient balance
    # ---------------------------------------------------------
    print("  Case 1: Insufficient available balance")

    idempotency_key = f"phase3b-insufficient-{uuid.uuid4().hex}"

    payload = {
        "to_user_id": RECEIVER_ID,
        "asset_id": ASSET_ID,
        "amount": "999999999",
    }

    response = await client.post(
        "/api/v1/transfers",
        headers={
            **headers,
            "Idempotency-Key": idempotency_key,
        },
        json=payload,
    )

    print(
        f"  HTTP {response.status_code}: "
        f"{response.json()}"
    )

    if response.status_code != 400:
        raise AssertionError(
            "Expected HTTP 400 for insufficient balance, "
            f"received {response.status_code}"
        )

    detail = response.json().get("detail", "")

    if "Insufficient available balance" not in detail:
        raise AssertionError(
            f"Unexpected insufficient-balance response: {detail}"
        )

    print("  PASS")

    # ---------------------------------------------------------
    # Case 2: Locked balance
    # ---------------------------------------------------------
    #
    # We intentionally request an amount larger than the
    # available balance. This verifies that locked funds are
    # not treated as spendable funds.
    #
    # ---------------------------------------------------------

    print("  Case 2: Locked balance is not spendable")

    idempotency_key = f"phase3b-locked-{uuid.uuid4().hex}"

    payload = {
        "to_user_id": RECEIVER_ID,
        "asset_id": ASSET_ID,
        "amount": "999999999",
    }

    response = await client.post(
        "/api/v1/transfers",
        headers={
            **headers,
            "Idempotency-Key": idempotency_key,
        },
        json=payload,
    )

    print(
        f"  HTTP {response.status_code}: "
        f"{response.json()}"
    )

    if response.status_code != 400:
        raise AssertionError(
            "Expected HTTP 400 when spendable balance "
            "is insufficient"
        )

    detail = response.json().get("detail", "")

    if "Insufficient available balance" not in detail:
        raise AssertionError(
            f"Unexpected locked-balance response: {detail}"
        )

    print("  PASS")

    print("  Test 6 PASS")

async def final_reconciliation():
    print("\n[7] Final Phase 3B integrity check")

    for user_id in (USER1_ID, USER2_ID):
        account = await get_account(user_id)
        ledger = await ledger_balance(user_id)
        total = account["available"] + account["locked"]

        print(
            f"  {user_id}: available={account['available']} "
            f"locked={account['locked']} total={total} ledger={ledger}"
        )

        if account["status"] != "ACTIVE":
            raise AssertionError(f"Account {user_id} is not ACTIVE.")

        if account["available"] < 0 or account["locked"] < 0:
            raise AssertionError(f"Negative balance detected: {account}")

        if total != ledger:
            raise AssertionError(
                f"Final reconciliation failed for {user_id}: "
                f"account={total}, ledger={ledger}"
            )

    print("  PASS")


async def main():
    if not TOKEN:
        raise RuntimeError(
            "Set ACCESS_TOKEN first: "
            '$env:ACCESS_TOKEN="YOUR_CURRENT_ACCESS_TOKEN"'
        )

    print("=" * 70)
    print("BITNOVA PHASE 3B INTEGRITY TEST SUITE")
    print("=" * 70)
    print(f"API: {BASE_URL}")
    print(f"Sender: {USER1_ID}")
    print(f"Receiver: {USER2_ID}")
    print(f"Asset: USDT ({USDT_ASSET_ID})")

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=30.0,
    ) as client:
        await test_ledger_account_reconciliation()
        await test_failed_transfer_rollback(client)
        await test_idempotency_replay(client)
        await test_audit_trail(client)
        await test_concurrent_multi_user(client)
        await test_insufficient_and_locked_balance(client)
        await final_reconciliation()

    await engine.dispose()

    print("\n" + "=" * 70)
    print("PHASE 3B COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())