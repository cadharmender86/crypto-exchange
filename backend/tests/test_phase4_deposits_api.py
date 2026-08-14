import asyncio
import os
import sys
import uuid
from pathlib import Path

import httpx

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1]),
)

BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

USER1_TOKEN = os.getenv("ACCESS_TOKEN")
USER2_TOKEN = os.getenv("USER2_ACCESS_TOKEN")

USDT_ASSET_ID = "87e6d426-afc4-4bad-b2f5-7c48efe74246"


def auth_headers(token):
    if not token:
        raise RuntimeError(
            "Required access token environment variable is not set"
        )

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


async def get_wallet_and_address(client, token):
    response = await client.get(
        "/api/v1/wallets",
        headers=auth_headers(token),
    )

    if response.status_code != 200:
        raise AssertionError(
            f"Unable to list wallets: "
            f"{response.status_code} {response.text}"
        )

    wallets = response.json()

    if not wallets:
        raise AssertionError(
            "Authenticated user has no wallet"
        )

    wallet = wallets[0]

    response = await client.get(
        f"/api/v1/wallets/{wallet['id']}/addresses",
        headers=auth_headers(token),
    )

    if response.status_code != 200:
        raise AssertionError(
            f"Unable to list wallet addresses: "
            f"{response.status_code} {response.text}"
        )

    addresses = response.json()

    matching = [
        address
        for address in addresses
        if (
            address["asset_id"] == USDT_ASSET_ID
            and address["network"] == "ETHEREUM"
            and address["status"] == "ACTIVE"
        )
    ]

    if not matching:
        raise AssertionError(
            "No active USDT/ETHEREUM deposit address"
        )

    return wallet, matching[0]


async def test_unauthenticated_create(client):
    print("\n[1] Unauthenticated deposit creation")

    response = await client.post(
        "/api/v1/deposits",
        json={
            "wallet_address_id": (
                "5144f696-ef65-4f7d-8057-c7a176108fca"
            ),
            "asset_id": USDT_ASSET_ID,
            "network": "ETHEREUM",
            "blockchain_tx_hash": (
                f"phase43-api-auth-{uuid.uuid4().hex}"
            ),
            "amount": "10",
        },
    )

    print(f"  HTTP {response.status_code}")

    if response.status_code != 401:
        raise AssertionError(
            f"Expected 401, got {response.status_code}"
        )

    print("  PASS")


async def test_valid_create_and_read(client):
    print("\n[2] User 1 creates and reads own deposit")

    _, address = await get_wallet_and_address(
        client,
        USER1_TOKEN,
    )

    tx_hash = (
        f"phase43-api-{uuid.uuid4().hex}"
    )

    response = await client.post(
        "/api/v1/deposits",
        headers=auth_headers(USER1_TOKEN),
        json={
            "wallet_address_id": address["id"],
            "asset_id": USDT_ASSET_ID,
            "network": "ETHEREUM",
            "blockchain_tx_hash": tx_hash,
            "amount": "10",
        },
    )

    print(f"  CREATE HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 201:
        raise AssertionError(
            f"Expected 201, got {response.status_code}"
        )

    deposit = response.json()
    deposit_id = deposit["id"]

    if deposit["status"] != "PENDING":
        raise AssertionError(
            f"Expected PENDING, got {deposit['status']}"
        )

    response = await client.get(
        f"/api/v1/deposits/{deposit_id}",
        headers=auth_headers(USER1_TOKEN),
    )

    print(f"  READ HTTP {response.status_code}")

    if response.status_code != 200:
        raise AssertionError(
            f"Expected 200, got {response.status_code}"
        )

    if response.json()["id"] != deposit_id:
        raise AssertionError(
            "Returned deposit ID does not match"
        )

    print("  PASS")

    return deposit


async def test_cross_user_deposit_access(client):
    print("\n[3] User 2 cannot access User 1 deposit")

    _, user1_address = await get_wallet_and_address(
        client,
        USER1_TOKEN,
    )

    tx_hash = (
        f"phase43-api-cross-user-{uuid.uuid4().hex}"
    )

    response = await client.post(
        "/api/v1/deposits",
        headers=auth_headers(USER1_TOKEN),
        json={
            "wallet_address_id": user1_address["id"],
            "asset_id": USDT_ASSET_ID,
            "network": "ETHEREUM",
            "blockchain_tx_hash": tx_hash,
            "amount": "5",
        },
    )

    if response.status_code != 201:
        raise AssertionError(
            f"Unable to create test deposit: "
            f"{response.status_code} {response.text}"
        )

    deposit_id = response.json()["id"]

    response = await client.get(
        f"/api/v1/deposits/{deposit_id}",
        headers=auth_headers(USER2_TOKEN),
    )

    print(f"  HTTP {response.status_code}")

    if response.status_code != 404:
        raise AssertionError(
            f"Expected 404 for cross-user access, "
            f"got {response.status_code}"
        )

    print("  PASS")


async def test_cross_user_wallet_address_rejected(client):
    print("\n[4] User 1 cannot create deposit using User 2 address")

    _, user2_address = await get_wallet_and_address(
        client,
        USER2_TOKEN,
    )

    response = await client.post(
        "/api/v1/deposits",
        headers=auth_headers(USER1_TOKEN),
        json={
            "wallet_address_id": user2_address["id"],
            "asset_id": USDT_ASSET_ID,
            "network": "ETHEREUM",
            "blockchain_tx_hash": (
                f"phase43-api-idor-{uuid.uuid4().hex}"
            ),
            "amount": "5",
        },
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code not in (400, 403, 404):
        raise AssertionError(
            "Cross-user wallet address was accepted: "
            f"HTTP {response.status_code}"
        )

    print("  PASS")


async def test_duplicate_transaction(client):
    print("\n[5] Duplicate transaction is idempotent")

    _, address = await get_wallet_and_address(
        client,
        USER1_TOKEN,
    )

    tx_hash = (
        f"phase43-api-duplicate-{uuid.uuid4().hex}"
    )

    payload = {
        "wallet_address_id": address["id"],
        "asset_id": USDT_ASSET_ID,
        "network": "ETHEREUM",
        "blockchain_tx_hash": tx_hash,
        "amount": "7",
    }

    first = await client.post(
        "/api/v1/deposits",
        headers=auth_headers(USER1_TOKEN),
        json=payload,
    )

    if first.status_code != 201:
        raise AssertionError(
            f"First create failed: "
            f"{first.status_code} {first.text}"
        )

    second = await client.post(
        "/api/v1/deposits",
        headers=auth_headers(USER1_TOKEN),
        json=payload,
    )

    print(f"  First:  {first.status_code}")
    print(f"  Second: {second.status_code}")

    if second.status_code != 201:
        raise AssertionError(
            f"Expected idempotent 201, "
            f"got {second.status_code}: {second.text}"
        )

    if first.json()["id"] != second.json()["id"]:
        raise AssertionError(
            "Duplicate request created another deposit"
        )

    print("  PASS")


async def test_invalid_amount(client):
    print("\n[6] Invalid amount rejected")

    _, address = await get_wallet_and_address(
        client,
        USER1_TOKEN,
    )

    response = await client.post(
        "/api/v1/deposits",
        headers=auth_headers(USER1_TOKEN),
        json={
            "wallet_address_id": address["id"],
            "asset_id": USDT_ASSET_ID,
            "network": "ETHEREUM",
            "blockchain_tx_hash": (
                f"phase43-api-invalid-{uuid.uuid4().hex}"
            ),
            "amount": "-1",
        },
    )

    print(f"  HTTP {response.status_code}")

    if response.status_code != 422:
        raise AssertionError(
            f"Expected 422, got {response.status_code}"
        )

    print("  PASS")


async def test_customer_cannot_confirm_or_credit(client):
    print("\n[7] Customer confirmation/credit endpoints unavailable")

    fake_id = str(uuid.uuid4())

    confirm = await client.post(
        f"/api/v1/deposits/{fake_id}/confirm",
        headers=auth_headers(USER1_TOKEN),
        json={"confirmations": 3},
    )

    credit = await client.post(
        f"/api/v1/deposits/{fake_id}/credit",
        headers=auth_headers(USER1_TOKEN),
    )

    print(
        f"  Confirm endpoint: {confirm.status_code}"
    )
    print(
        f"  Credit endpoint:  {credit.status_code}"
    )

    if confirm.status_code not in (404, 405):
        raise AssertionError(
            "Customer confirmation endpoint is exposed"
        )

    if credit.status_code not in (404, 405):
        raise AssertionError(
            "Customer credit endpoint is exposed"
        )

    print("  PASS")


async def main():
    if not USER1_TOKEN:
        raise RuntimeError(
            "ACCESS_TOKEN is not set"
        )

    if not USER2_TOKEN:
        raise RuntimeError(
            "USER2_ACCESS_TOKEN is not set"
        )

    print("=" * 70)
    print("BITNOVA PHASE 4.3 DEPOSIT API SECURITY TEST")
    print("=" * 70)

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=10,
    ) as client:

        await test_unauthenticated_create(client)
        await test_valid_create_and_read(client)
        await test_cross_user_deposit_access(client)
        await test_cross_user_wallet_address_rejected(client)
        await test_duplicate_transaction(client)
        await test_invalid_amount(client)
        await test_customer_cannot_confirm_or_credit(client)

    print("\n" + "=" * 70)
    print("PHASE 4.3 DEPOSIT API SECURITY TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())