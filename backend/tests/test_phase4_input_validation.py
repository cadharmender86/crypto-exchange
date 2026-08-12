import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
import asyncio
import uuid
from decimal import Decimal

import httpx

from app.core.config import settings


BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

TOKEN = os.getenv("ACCESS_TOKEN")

SENDER_ID = "955767f7-fa07-4d10-ba04-75d8757b1e57"
RECEIVER_ID = "60df3023-8a8d-4910-98c7-b005fa1b744c"

USDT_ASSET_ID = "87e6d426-afc4-4bad-b2f5-7c48efe74246"


def auth_headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }


def idem_key(name):
    return f"phase4-input-{name}-{uuid.uuid4().hex}"


async def transfer(client, payload, name):
    response = await client.post(
        "/api/v1/transfers",
        headers={
            **auth_headers(),
            "Idempotency-Key": idem_key(name),
        },
        json=payload,
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    return response


async def test_missing_to_user_id(client):
    print("\n[1] Missing to_user_id")

    response = await transfer(
        client,
        {
            "asset_id": USDT_ASSET_ID,
            "amount": "1",
        },
        "missing-to-user",
    )

    if response.status_code != 422:
        raise AssertionError(
            f"Expected 422, received {response.status_code}"
        )

    print("  PASS")


async def test_missing_asset_id(client):
    print("\n[2] Missing asset_id")

    response = await transfer(
        client,
        {
            "to_user_id": RECEIVER_ID,
            "amount": "1",
        },
        "missing-asset",
    )

    if response.status_code != 422:
        raise AssertionError(
            f"Expected 422, received {response.status_code}"
        )

    print("  PASS")


async def test_missing_amount(client):
    print("\n[3] Missing amount")

    response = await transfer(
        client,
        {
            "to_user_id": RECEIVER_ID,
            "asset_id": USDT_ASSET_ID,
        },
        "missing-amount",
    )

    if response.status_code != 422:
        raise AssertionError(
            f"Expected 422, received {response.status_code}"
        )

    print("  PASS")


async def test_invalid_uuid(client):
    print("\n[4] Invalid UUID")

    response = await transfer(
        client,
        {
            "to_user_id": "not-a-uuid",
            "asset_id": USDT_ASSET_ID,
            "amount": "1",
        },
        "invalid-uuid",
    )

    if response.status_code != 422:
        raise AssertionError(
            f"Expected 422, received {response.status_code}"
        )

    print("  PASS")


async def test_nonexistent_user(client):
    print("\n[5] Non-existent destination user")

    fake_user = str(uuid.uuid4())

    response = await transfer(
        client,
        {
            "to_user_id": fake_user,
            "asset_id": USDT_ASSET_ID,
            "amount": "1",
        },
        "fake-user",
    )

    if response.status_code not in (400, 404):
        raise AssertionError(
            f"Expected 400/404, received {response.status_code}"
        )

    print("  PASS")


async def test_nonexistent_asset(client):
    print("\n[6] Non-existent asset")

    fake_asset = str(uuid.uuid4())

    response = await transfer(
        client,
        {
            "to_user_id": RECEIVER_ID,
            "asset_id": fake_asset,
            "amount": "1",
        },
        "fake-asset",
    )

    if response.status_code not in (400, 404):
        raise AssertionError(
            f"Expected 400/404, received {response.status_code}"
        )

    print("  PASS")


async def test_zero_amount(client):
    print("\n[7] Zero amount")

    response = await transfer(
        client,
        {
            "to_user_id": RECEIVER_ID,
            "asset_id": USDT_ASSET_ID,
            "amount": "0",
        },
        "zero",
    )

    if response.status_code not in (400, 422):
        raise AssertionError(
            f"Expected 400/422, received {response.status_code}"
        )

    print("  PASS")


async def test_negative_amount(client):
    print("\n[8] Negative amount")

    response = await transfer(
        client,
        {
            "to_user_id": RECEIVER_ID,
            "asset_id": USDT_ASSET_ID,
            "amount": "-10",
        },
        "negative",
    )

    if response.status_code not in (400, 422):
        raise AssertionError(
            f"Expected 400/422, received {response.status_code}"
        )

    print("  PASS")


async def test_huge_amount(client):
    print("\n[9] Extremely large amount")

    response = await transfer(
        client,
        {
            "to_user_id": RECEIVER_ID,
            "asset_id": USDT_ASSET_ID,
            "amount": "999999999999999999999999999999999999999999",
        },
        "huge",
    )

    if response.status_code not in (400, 422):
        raise AssertionError(
            f"Expected 400/422, received {response.status_code}"
        )

    print("  PASS")


async def test_excessive_precision(client):
    print("\n[10] Excessive decimal precision")

    response = await transfer(
        client,
        {
            "to_user_id": RECEIVER_ID,
            "asset_id": USDT_ASSET_ID,
            "amount": "1.123456789012345678901234567890",
        },
        "precision",
    )

    if response.status_code not in (400, 422):
        raise AssertionError(
            f"Expected 400/422, received {response.status_code}"
        )

    print("  PASS")


async def test_null_amount(client):
    print("\n[11] Null amount")

    response = await transfer(
        client,
        {
            "to_user_id": RECEIVER_ID,
            "asset_id": USDT_ASSET_ID,
            "amount": None,
        },
        "null",
    )

    if response.status_code != 422:
        raise AssertionError(
            f"Expected 422, received {response.status_code}"
        )

    print("  PASS")


async def test_invalid_amount_type(client):
    print("\n[12] Invalid amount type")

    response = await transfer(
        client,
        {
            "to_user_id": RECEIVER_ID,
            "asset_id": USDT_ASSET_ID,
            "amount": {
                "value": "100"
            },
        },
        "invalid-type",
    )

    if response.status_code != 422:
        raise AssertionError(
            f"Expected 422, received {response.status_code}"
        )

    print("  PASS")


async def test_empty_body(client):
    print("\n[13] Empty request body")

    response = await client.post(
        "/api/v1/transfers",
        headers={
            **auth_headers(),
            "Idempotency-Key": idem_key("empty-body"),
        },
        json={},
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 422:
        raise AssertionError(
            f"Expected 422, received {response.status_code}"
        )

    print("  PASS")


async def test_extra_fields(client):
    print("\n[14] Unexpected extra field")

    response = await transfer(
        client,
        {
            "to_user_id": RECEIVER_ID,
            "asset_id": USDT_ASSET_ID,
            "amount": "1",
            "admin": True,
        },
        "extra-field",
    )

    print("  Checking API behavior for extra field")

    if response.status_code == 201:
        print(
            "  PASS - request succeeded; "
            "extra field was not used for authorization"
        )
    elif response.status_code in (400, 422):
        print(
            "  PASS - extra field rejected"
        )
    else:
        raise AssertionError(
            f"Unexpected HTTP {response.status_code}"
        )


async def test_self_transfer(client):
    print("\n[15] Self transfer")

    response = await transfer(
        client,
        {
            "to_user_id": SENDER_ID,
            "asset_id": USDT_ASSET_ID,
            "amount": "1",
        },
        "self-transfer",
    )

    if response.status_code != 400:
        raise AssertionError(
            f"Expected 400, received {response.status_code}"
        )

    print("  PASS")


async def test_insufficient_balance(client):
    print("\n[16] Insufficient balance")

    response = await transfer(
        client,
        {
            "to_user_id": RECEIVER_ID,
            "asset_id": USDT_ASSET_ID,
            "amount": "999999999",
        },
        "insufficient",
    )

    if response.status_code != 400:
        raise AssertionError(
            f"Expected 400, received {response.status_code}"
        )

    print("  PASS")


async def test_invalid_requests_do_not_change_balance(client):
    print("\n[17] Invalid request must not change balance")

    before = await client.get(
        "/api/v1/accounts",
        headers=auth_headers(),
    )

    if before.status_code != 200:
        raise AssertionError(
            f"Unable to read account before test: "
            f"{before.status_code}"
        )

    accounts_before = before.json()

    sender_before = next(
        account
        for account in accounts_before
        if account["asset_id"] == USDT_ASSET_ID
    )

    balance_before = Decimal(
        str(sender_before["available_balance"])
    )

    response = await transfer(
        client,
        {
            "to_user_id": RECEIVER_ID,
            "asset_id": USDT_ASSET_ID,
            "amount": "-500",
        },
        "balance-integrity",
    )

    if response.status_code not in (400, 422):
        raise AssertionError(
            "Invalid transfer was unexpectedly accepted"
        )

    after = await client.get(
        "/api/v1/accounts",
        headers=auth_headers(),
    )

    if after.status_code != 200:
        raise AssertionError(
            f"Unable to read account after test: "
            f"{after.status_code}"
        )

    accounts_after = after.json()

    sender_after = next(
        account
        for account in accounts_after
        if account["asset_id"] == USDT_ASSET_ID
    )

    balance_after = Decimal(
        str(sender_after["available_balance"])
    )

    print(f"  Balance before: {balance_before}")
    print(f"  Balance after : {balance_after}")

    if balance_before != balance_after:
        raise AssertionError(
            "CRITICAL: invalid request changed account balance"
        )

    print("  PASS")


async def main():

    print("=" * 70)
    print("BITNOVA PHASE 4.3 INPUT VALIDATION / ABUSE TEST SUITE")
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
        timeout=15,
    ) as client:

        await test_missing_to_user_id(client)
        await test_missing_asset_id(client)
        await test_missing_amount(client)
        await test_invalid_uuid(client)
        await test_nonexistent_user(client)
        await test_nonexistent_asset(client)
        await test_zero_amount(client)
        await test_negative_amount(client)
        await test_huge_amount(client)
        await test_excessive_precision(client)
        await test_null_amount(client)
        await test_invalid_amount_type(client)
        await test_empty_body(client)
        await test_extra_fields(client)
        await test_self_transfer(client)
        await test_insufficient_balance(client)
        await test_invalid_requests_do_not_change_balance(client)

    print("\n" + "=" * 70)
    print("PHASE 4.3 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())