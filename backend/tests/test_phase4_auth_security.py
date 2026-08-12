import os
import uuid
import asyncio
from datetime import datetime, timedelta, timezone

import httpx
from jose import jwt
import sys
sys.path.insert(0, ".")

from app.core.config import settings


BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

USER1_ID = "955767f7-fa07-4d10-ba04-75d8757b1e57"


def auth_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


async def test_valid_access_token(client):
    print("\n[1] Valid access token")

    if not ACCESS_TOKEN:
        raise AssertionError("ACCESS_TOKEN is not set")

    response = await client.get(
        "/api/v1/accounts",
        headers=auth_headers(ACCESS_TOKEN),
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code == 401:
        raise AssertionError(
            "Valid access token was rejected"
        )

    print("  PASS")


async def test_missing_token(client):
    print("\n[2] Missing Authorization token")

    response = await client.get(
        "/api/v1/accounts"
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 401:
        raise AssertionError(
            f"Expected 401, received {response.status_code}"
        )

    print("  PASS")


async def test_malformed_token(client):
    print("\n[3] Malformed JWT")

    response = await client.get(
        "/api/v1/accounts",
        headers={
            "Authorization": "Bearer this-is-not-a-jwt",
            "Content-Type": "application/json",
        },
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 401:
        raise AssertionError(
            f"Expected 401, received {response.status_code}"
        )

    print("  PASS")


async def test_invalid_signature(client):
    print("\n[4] Invalid JWT signature")

    if not ACCESS_TOKEN:
        raise AssertionError("ACCESS_TOKEN is not set")

    payload = jwt.decode(
        ACCESS_TOKEN,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    forged_token = jwt.encode(
        payload,
        "WRONG_SECRET_KEY_FOR_TESTING",
        algorithm=settings.jwt_algorithm,
    )

    response = await client.get(
        "/api/v1/accounts",
        headers=auth_headers(forged_token),
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 401:
        raise AssertionError(
            f"Expected 401, received {response.status_code}"
        )

    print("  PASS")


async def test_expired_token(client):
    print("\n[5] Expired JWT")

    payload = {
        "sub": USER1_ID,
        "type": "access",
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }

    expired_token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = await client.get(
        "/api/v1/accounts",
        headers=auth_headers(expired_token),
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 401:
        raise AssertionError(
            f"Expected 401, received {response.status_code}"
        )

    print("  PASS")


async def test_refresh_token_as_access(client):
    print("\n[6] Refresh token used as access token")

    if not REFRESH_TOKEN:
        print("  SKIPPED - REFRESH_TOKEN is not set")
        return

    response = await client.get(
        "/api/v1/accounts",
        headers=auth_headers(REFRESH_TOKEN),
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 401:
        raise AssertionError(
            "Refresh token was incorrectly accepted as access token"
        )

    print("  PASS")


async def test_wrong_algorithm(client):
    print("\n[7] JWT with wrong algorithm")

    payload = {
        "sub": USER1_ID,
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    forged_token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm="HS384",
    )

    response = await client.get(
        "/api/v1/accounts",
        headers=auth_headers(forged_token),
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code != 401:
        raise AssertionError(
            f"Expected 401, received {response.status_code}"
        )

    print("  PASS")


async def test_fake_user(client):
    print("\n[8] JWT containing non-existent user")

    fake_user_id = str(uuid.uuid4())

    payload = {
        "sub": fake_user_id,
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    fake_token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = await client.get(
        "/api/v1/accounts",
        headers=auth_headers(fake_token),
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text}")

    if response.status_code not in (401, 403):
        raise AssertionError(
            f"Expected 401/403, received {response.status_code}"
        )

    print("  PASS")


async def main():
    print("=" * 70)
    print("BITNOVA PHASE 4.1 AUTHENTICATION SECURITY TEST SUITE")
    print("=" * 70)
    print(f"API: {BASE_URL}")
    print(f"User: {USER1_ID}")

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=15.0,
    ) as client:

        await test_valid_access_token(client)
        await test_missing_token(client)
        await test_malformed_token(client)
        await test_invalid_signature(client)
        await test_expired_token(client)
        await test_refresh_token_as_access(client)
        await test_wrong_algorithm(client)
        await test_fake_user(client)

    print("\n" + "=" * 70)
    print("PHASE 4.1 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())