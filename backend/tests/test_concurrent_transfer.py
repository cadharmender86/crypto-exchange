import asyncio
import os
import uuid

import httpx


BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

USER_1_ID = "955767f7-fa07-4d10-ba04-75d8757b1e57"
USER_2_ID = "35712d6a-2c16-476f-be18-9c9d8206efac"

USDT_ASSET_ID = "87e6d426-afc4-4bad-b2f5-7c48efe74246"

TRANSFER_AMOUNT = 1000


async def make_transfer(client: httpx.AsyncClient, request_name: str):
    idempotency_key = (
        f"concurrency-{request_name}-{uuid.uuid4().hex}"
    )

    payload = {
        "to_user_id": USER_2_ID,
        "asset_id": USDT_ASSET_ID,
        "amount": TRANSFER_AMOUNT,
        "description": (
            f"Concurrent locking test - {request_name}"
        ),
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Idempotency-Key": idempotency_key,
    }

    print(f"\n[{request_name}] Sending request")
    print(f"[{request_name}] Idempotency-Key: {idempotency_key}")

    response = await client.post(
        "/api/v1/transfers",
        json=payload,
        headers=headers,
    )

    print(
        f"[{request_name}] "
        f"HTTP {response.status_code}"
    )

    try:
        body = response.json()
    except Exception:
        body = response.text

    print(f"[{request_name}] Response: {body}")

    return {
        "name": request_name,
        "status_code": response.status_code,
        "body": body,
    }


async def main():
    if not ACCESS_TOKEN:
        raise RuntimeError(
            "ACCESS_TOKEN environment variable is not set."
        )

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=30.0,
    ) as client:

        print("=" * 70)
        print("CONCURRENT TRANSFER / ACCOUNT LOCKING TEST")
        print("=" * 70)

        print(f"Sender:      {USER_1_ID}")
        print(f"Receiver:    {USER_2_ID}")
        print(f"Asset:       USDT")
        print(f"Amount each: {TRANSFER_AMOUNT}")
        print("")

        results = await asyncio.gather(
            make_transfer(client, "REQUEST-A"),
            make_transfer(client, "REQUEST-B"),
        )

        print("\n" + "=" * 70)
        print("TEST RESULT")
        print("=" * 70)

        successful = [
            result
            for result in results
            if result["status_code"] in (200, 201)
        ]

        failed = [
            result
            for result in results
            if result["status_code"] not in (200, 201)
        ]

        print(f"Successful requests: {len(successful)}")
        print(f"Failed requests:     {len(failed)}")

        if len(successful) == 1 and len(failed) == 1:
            print("\nPASS")
            print(
                "Account locking prevented "
                "the double-spend."
            )
        elif len(successful) == 2:
            print("\nFAIL")
            print(
                "Both transfers succeeded. "
                "Possible double-spend vulnerability."
            )
        else:
            print("\nCHECK")
            print(
                "Unexpected result. Review the responses."
            )


if __name__ == "__main__":
    asyncio.run(main())
    