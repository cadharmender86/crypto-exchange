import sys
from pathlib import Path

# Allow imports from backend/app when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
import asyncio
import uuid
from decimal import Decimal

import httpx
from jose import jwt

from app.core.config import settings


BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

USER1_TOKEN = os.getenv("ACCESS_TOKEN")
USER2_TOKEN = os.getenv("USER2_ACCESS_TOKEN")

USER1_ID = "955767f7-fa07-4d10-ba04-75d8757b1e57"
USER2_ID = "c965beb6-a9c1-46ee-9d35-3a4ac516bc39"

USDT_ASSET_ID = "87e6d426-afc4-4bad-b2f5-7c48efe74246"

USER1_ACCOUNT_ID = "ab51fffa-a1c5-48a2-8795-2146c0d5943b"


def headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


async def test_user1_own_accounts(client):
    print("\n[1] User 1 accessing own accounts")

    response = await client.get(
        "/api/v1/accounts",
        headers=headers(USER1_TOKEN),
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 200:
        raise AssertionError(
            f"User 1 should access own accounts. "
            f"Received {response.status_code}"
        )

    print("  PASS")


async def test_user1_own_profile(client):
    print("\n[2] User 1 accessing own profile")

    response = await client.get(
        f"/api/v1/users/{USER1_ID}",
        headers=headers(USER1_TOKEN),
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 200:
        raise AssertionError(
            f"User 1 should access own profile. "
            f"Received {response.status_code}"
        )

    print("  PASS")


async def test_user1_access_user2_profile(client):
    print("\n[3] User 1 attempting to access User 2 profile")

    response = await client.get(
        f"/api/v1/users/{USER2_ID}",
        headers=headers(USER1_TOKEN),
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code == 200:
        data = response.json()

        returned_user_id = data.get("id")

        if returned_user_id == USER2_ID:
            raise AssertionError(
                "CRITICAL IDOR: User 1 received User 2's profile"
            )

        if returned_user_id == USER1_ID:
            print(
                "  PASS - endpoint returned authenticated user's "
                "profile, not User 2's profile"
            )
            return

    if response.status_code in (403, 404):
        print("  PASS - cross-user access rejected")
        return

    raise AssertionError(
        f"Unexpected authorization behavior: "
        f"HTTP {response.status_code}"
    )


async def test_user2_own_profile(client):
    print("\n[4] User 2 accessing own profile")

    response = await client.get(
        f"/api/v1/users/{USER2_ID}",
        headers=headers(USER2_TOKEN),
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 200:
        raise AssertionError(
            f"User 2 should access own profile. "
            f"Received {response.status_code}"
        )

    print("  PASS")


async def test_user1_ledger_own_account(client):
    print("\n[5] User 1 accessing own ledger")

    response = await client.get(
        f"/api/v1/ledger/accounts/{USER1_ACCOUNT_ID}/entries",
        headers=headers(USER1_TOKEN),
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 200:
        raise AssertionError(
            "User 1 should access own ledger. "
            f"Received {response.status_code}"
        )

    print("  PASS")


async def test_user1_ledger_user2_account(client):
    print("\n[6] User 1 attempting to access User 2 ledger")

    # We need User 2's actual account ID.
    response = await client.get(
        "/api/v1/accounts",
        headers=headers(USER2_TOKEN),
    )

    if response.status_code != 200:
        raise AssertionError(
            f"Unable to retrieve User 2 account for test: "
            f"{response.status_code}"
        )

    accounts = response.json()

    if not accounts:
        raise AssertionError("User 2 has no account")

    user2_account_id = accounts[0]["id"]

    print(f"  User 2 account: {user2_account_id}")

    response = await client.get(
        f"/api/v1/ledger/accounts/{user2_account_id}/entries",
        headers=headers(USER1_TOKEN),
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code not in (403, 404):
        raise AssertionError(
            "Potential IDOR vulnerability: "
            "User 1 accessed User 2 ledger"
        )

    print("  PASS - cross-user ledger access rejected")


async def test_user1_transfer_to_user2(client):
    print("\n[7] User 1 transferring to User 2")

    payload = {
        "to_user_id": USER2_ID,
        "asset_id": USDT_ASSET_ID,
        "amount": "0.01",
    }

    response = await client.post(
        "/api/v1/transfers",
        headers={
            **headers(USER1_TOKEN),
            "Idempotency-Key":
                f"phase4-user1-user2-{uuid.uuid4().hex}",
        },
        json=payload,
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 201:
        raise AssertionError(
            "Legitimate User 1 -> User 2 transfer failed"
        )

    print("  PASS")


async def test_user2_transfer_to_user1(client):
    print("\n[8] User 2 transferring to User 1")

    payload = {
        "to_user_id": USER1_ID,
        "asset_id": USDT_ASSET_ID,
        "amount": "0.01",
    }

    response = await client.post(
        "/api/v1/transfers",
        headers={
            **headers(USER2_TOKEN),
            "Idempotency-Key":
                f"phase4-user2-user1-{uuid.uuid4().hex}",
        },
        json=payload,
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 201:
        raise AssertionError(
            "Legitimate User 2 -> User 1 transfer failed"
        )

    print("  PASS")


async def test_fake_user_transfer(client):
    print("\n[9] Transfer to non-existent user")

    fake_user_id = str(uuid.uuid4())

    payload = {
        "to_user_id": fake_user_id,
        "asset_id": USDT_ASSET_ID,
        "amount": "1",
    }

    response = await client.post(
        "/api/v1/transfers",
        headers={
            **headers(USER1_TOKEN),
            "Idempotency-Key":
                f"phase4-fake-user-{uuid.uuid4().hex}",
        },
        json=payload,
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code not in (400, 404):
        raise AssertionError(
            "Transfer to non-existent user was not rejected"
        )

    print("  PASS")


async def test_same_user_transfer(client):
    print("\n[10] User 1 attempting transfer to itself")

    payload = {
        "to_user_id": USER1_ID,
        "asset_id": USDT_ASSET_ID,
        "amount": "1",
    }

    response = await client.post(
        "/api/v1/transfers",
        headers={
            **headers(USER1_TOKEN),
            "Idempotency-Key":
                f"phase4-self-transfer-{uuid.uuid4().hex}",
        },
        json=payload,
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 400:
        raise AssertionError(
            f"Expected self-transfer to be rejected, "
            f"received {response.status_code}"
        )

    print("  PASS")


async def test_missing_token(client):
    print("\n[11] Cross-user endpoint without authentication")

    response = await client.get(
        f"/api/v1/users/{USER2_ID}"
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 401:
        raise AssertionError(
            f"Expected 401, received {response.status_code}"
        )

    print("  PASS")


async def main():

    print("=" * 70)
    print("BITNOVA PHASE 4.2 AUTHORIZATION / IDOR SECURITY TEST SUITE")
    print("=" * 70)

    print(f"API: {BASE_URL}")
    print(f"User 1: {USER1_ID}")
    print(f"User 2: {USER2_ID}")

    if not USER1_TOKEN:
        raise AssertionError(
            "ACCESS_TOKEN environment variable is not set"
        )

    if not USER2_TOKEN:
        raise AssertionError(
            "USER2_ACCESS_TOKEN environment variable is not set"
        )

    # Verify JWT identities before testing authorization.
    user1_payload = jwt.decode(
        USER1_TOKEN,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    user2_payload = jwt.decode(
        USER2_TOKEN,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    print(f"Token A user: {user1_payload.get('sub')}")
    print(f"Token B user: {user2_payload.get('sub')}")

    if user1_payload.get("sub") != USER1_ID:
        raise AssertionError(
            "ACCESS_TOKEN does not belong to User 1"
        )

    if user2_payload.get("sub") != USER2_ID:
        raise AssertionError(
            "USER2_ACCESS_TOKEN does not belong to User 2"
        )

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=15,
    ) as client:

        await test_user1_own_accounts(client)
        await test_user1_own_profile(client)
        await test_user1_access_user2_profile(client)
        await test_user2_own_profile(client)

        await test_user1_ledger_own_account(client)
        await test_user1_ledger_user2_account(client)

        await test_user1_transfer_to_user2(client)
        await test_user2_transfer_to_user1(client)

        await test_fake_user_transfer(client)
        await test_same_user_transfer(client)

        await test_missing_token(client)

    print("\n" + "=" * 70)
    print("PHASE 4.2 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())