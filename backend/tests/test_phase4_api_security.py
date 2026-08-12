import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncio
import json
import os
import uuid

import httpx


BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

TOKEN = os.getenv("ACCESS_TOKEN")

USER_ID = "955767f7-fa07-4d10-ba04-75d8757b1e57"

# Existing API endpoint from your OpenAPI output.
INTERNAL_DEPOSIT_ENDPOINT = (
    "/api/v1/internal/test-deposits"
)

LOGIN_ENDPOINT = "/api/v1/auth/login"

SENSITIVE_ENDPOINTS = [
    "/api/v1/accounts",
    "/api/v1/transfers",
]


# ============================================================
# HELPERS
# ============================================================

def auth_headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
    }


def print_result(name, status, detail=""):
    print(f"  {name}: {status}")

    if detail:
        print(f"    {detail}")


# ============================================================
# 1. SECURITY HEADERS
# ============================================================

async def test_security_headers(client):
    print("\n" + "=" * 70)
    print("[1] SECURITY HEADERS")
    print("=" * 70)

    response = await client.get("/api/v1/health")

    headers = {
        key.lower(): value
        for key, value in response.headers.items()
    }

    expected_headers = {
        "x-content-type-options": "nosniff",
        "x-frame-options": None,
        "content-security-policy": None,
        "referrer-policy": None,
    }

    failures = []

    for header, expected in expected_headers.items():

        value = headers.get(header)

        if value is None:
            print_result(
                header,
                "MISSING",
            )
            failures.append(header)

        elif expected is not None and value.lower() != expected.lower():
            print_result(
                header,
                "INVALID",
                f"received={value}",
            )
            failures.append(header)

        else:
            print_result(
                header,
                "PASS",
                value,
            )

    # HSTS should normally be present when deployed over HTTPS.
    # Local HTTP development is allowed to report a warning.
    if "strict-transport-security" not in headers:
        print_result(
            "strict-transport-security",
            "WARN",
            "Expected in HTTPS production",
        )

    if failures:
        print(
            f"\n  SECURITY FINDING: "
            f"{len(failures)} security header(s) missing/invalid"
        )
    else:
        print("\n  PASS - required headers present")


# ============================================================
# 2. CORS
# ============================================================

async def test_cors(client):
    print("\n" + "=" * 70)
    print("[2] CORS POLICY")
    print("=" * 70)

    malicious_origin = "https://evil.example"

    response = await client.get(
        "/api/v1/health",
        headers={
            "Origin": malicious_origin,
        },
    )

    allow_origin = response.headers.get(
        "access-control-allow-origin"
    )

    allow_credentials = response.headers.get(
        "access-control-allow-credentials"
    )

    print(
        f"  Origin tested: {malicious_origin}"
    )

    print(
        f"  Access-Control-Allow-Origin: "
        f"{allow_origin}"
    )

    print(
        f"  Access-Control-Allow-Credentials: "
        f"{allow_credentials}"
    )

    if allow_origin == "*":

        if allow_credentials == "true":
            print(
                "  FAIL - wildcard CORS with credentials"
            )
        else:
            print(
                "  WARN - wildcard CORS policy"
            )

    elif allow_origin == malicious_origin:

        print(
            "  FAIL - arbitrary malicious origin allowed"
        )

    else:

        print(
            "  PASS - malicious origin not allowed"
        )


# ============================================================
# 3. INTERNAL TEST-DEPOSIT ENDPOINT
# ============================================================

async def test_internal_endpoint_protection(client):
    print("\n" + "=" * 70)
    print("[3] INTERNAL TEST-DEPOSIT ENDPOINT")
    print("=" * 70)

    payload = {
        "user_id": USER_ID,
        "asset_id": "87e6d426-afc4-4bad-b2f5-7c48efe74246",
        "amount": "0.000001",
    }

    # IMPORTANT:
    # We intentionally do NOT send Authorization.
    # We must verify an internal money-creation endpoint
    # cannot be called anonymously.
    response = await client.post(
        INTERNAL_DEPOSIT_ENDPOINT,
        json=payload,
    )

    print(
        f"  Anonymous request: "
        f"HTTP {response.status_code}"
    )

    print(
        f"  Response: {response.text[:500]}"
    )

    if response.status_code in (401, 403):

        print(
            "  PASS - internal endpoint requires authorization"
        )

    elif response.status_code in (404, 405):

        print(
            "  PASS - endpoint unavailable externally"
        )

    elif response.status_code in (422,):

        print(
            "  FAIL - endpoint appears reachable; "
            "request was rejected only by validation"
        )

    elif response.status_code in (200, 201):

        print(
            "  CRITICAL FAIL - anonymous caller "
            "can reach money-creation endpoint"
        )

    else:

        print(
            "  REVIEW - endpoint returned "
            f"HTTP {response.status_code}"
        )


# ============================================================
# 4. SENSITIVE ENDPOINT WITHOUT AUTH
# ============================================================

async def test_missing_auth_on_sensitive_endpoints(client):
    print("\n" + "=" * 70)
    print("[4] AUTHENTICATION ENFORCEMENT")
    print("=" * 70)

    for endpoint in SENSITIVE_ENDPOINTS:

        if endpoint.endswith("/transfers"):

            response = await client.post(
                endpoint,
                json={
                    "to_user_id":
                        "60df3023-8a8d-4910-98c7-b005fa1b744c",
                    "asset_id":
                        "87e6d426-afc4-4bad-b2f5-7c48efe74246",
                    "amount": "1",
                },
            )

        else:

            response = await client.get(
                endpoint
            )

        print(
            f"  {endpoint}: "
            f"HTTP {response.status_code}"
        )

        if response.status_code in (401, 403):

            print(
                "    PASS - authentication required"
            )

        elif response.status_code in (
            200,
            201,
        ):

            print(
                "    CRITICAL FAIL - "
                "unauthenticated access allowed"
            )

        else:

            print(
                "    REVIEW - endpoint returned "
                f"{response.status_code}"
            )


# ============================================================
# 5. METHOD ABUSE
# ============================================================

async def test_http_method_abuse(client):
    print("\n" + "=" * 70)
    print("[5] HTTP METHOD ABUSE")
    print("=" * 70)

    tests = [
        (
            "GET transfer endpoint",
            "get",
            "/api/v1/transfers",
        ),
        (
            "DELETE accounts endpoint",
            "delete",
            "/api/v1/accounts",
        ),
        (
            "PUT health endpoint",
            "put",
            "/api/v1/health",
        ),
        (
            "PATCH health endpoint",
            "patch",
            "/api/v1/health",
        ),
    ]

    for name, method, endpoint in tests:

        request_method = getattr(
            client,
            method,
        )

        response = await request_method(
            endpoint,
            headers=auth_headers()
            if TOKEN
            else {},
        )

        print(
            f"  {name}: "
            f"HTTP {response.status_code}"
        )

        if response.status_code == 405:

            print("    PASS - method rejected")

        elif response.status_code in (
            401,
            403,
        ):

            print(
                "    PASS - protected/rejected"
            )

        elif response.status_code in (
            200,
            201,
        ):

            print(
                "    REVIEW - unexpected method accepted"
            )

        else:

            print(
                "    REVIEW"
            )


# ============================================================
# 6. INFORMATION LEAKAGE
# ============================================================

async def test_information_leakage(client):
    print("\n" + "=" * 70)
    print("[6] INFORMATION LEAKAGE")
    print("=" * 70)

    malicious_payloads = [
        {
            "name": "SQL-like input",
            "value": "' OR '1'='1",
        },
        {
            "name": "Path traversal",
            "value": "../../etc/passwd",
        },
        {
            "name": "Stack trace probe",
            "value": "__import__('os').system('whoami')",
        },
        {
            "name": "HTML injection",
            "value": "<script>alert(1)</script>",
        },
    ]

    leaked_terms = [
        "traceback",
        "sqlalchemy",
        "asyncpg",
        "postgresql",
        "password_hash",
        "secret_key",
        "jwt_secret",
        "file not found",
        "c:\\users\\",
        "/app/",
    ]

    for item in malicious_payloads:

        response = await client.post(
            LOGIN_ENDPOINT,
            data={
                "username": item["value"],
                "password": "invalid-password",
            },
        )

        body = response.text.lower()

        leaks = [
            term
            for term in leaked_terms
            if term.lower() in body
        ]

        print(
            f"  {item['name']}: "
            f"HTTP {response.status_code}"
        )

        if leaks:

            print(
                f"    FAIL - possible information leakage: "
                f"{leaks}"
            )

        else:

            print(
                "    PASS - no obvious internal details"
            )


# ============================================================
# 7. MALFORMED JSON
# ============================================================

async def test_malformed_json(client):
    print("\n" + "=" * 70)
    print("[7] MALFORMED JSON HANDLING")
    print("=" * 70)

    response = await client.post(
        "/api/v1/transfers",
        headers={
            **auth_headers(),
            "Content-Type": "application/json",
        },
        content=b'{"broken": ',
    )

    print(
        f"  HTTP {response.status_code}"
    )

    print(
        f"  Response: "
        f"{response.text[:500]}"
    )

    if response.status_code in (
        400,
        401,
        403,
        422,
    ):

        print(
            "  PASS - malformed JSON rejected safely"
        )

    elif response.status_code >= 500:

        print(
            "  FAIL - malformed request caused "
            "server error"
        )

    else:

        print(
            "  REVIEW"
        )

# ============================================================
# 8. OVERSIZED IDEMPOTENCY KEY
# ============================================================

async def test_oversized_idempotency_key(client):
    print("\n" + "=" * 70)
    print("[8] OVERSIZED IDEMPOTENCY KEY")
    print("=" * 70)

    # API contract: Idempotency-Key max_length=100
    oversized_key = "A" * 101

    print(f"  Idempotency-Key length: {len(oversized_key)}")
    print("  Expected maximum length: 100")

    response = await client.post(
        "/api/v1/transfers",
        headers={
            **auth_headers(),
            "Idempotency-Key": oversized_key,
            "Content-Type": "application/json",
        },
        json={
            "to_user_id": "60df3023-8a8d-4910-98c7-b005fa1b744c",
            "asset_id": "87e6d426-afc4-4bad-b2f5-7c48efe74246",
            "amount": "1",
        },
    )

    print(f"  HTTP {response.status_code}")
    print(f"  Response: {response.text[:500]}")

    # FastAPI Header(max_length=100) should reject this
    # before TransferService.transfer() is executed.
    if response.status_code == 422:
        print("  PASS - oversized key rejected by request validation")

    elif response.status_code >= 500:
        print("  FAIL - oversized header caused server error")
        raise AssertionError(
            "Oversized Idempotency-Key caused a server error"
        )

    elif response.status_code in (400, 401, 403, 413):
        print(
            "  WARN - oversized key rejected, "
            "but not by expected FastAPI validation"
        )

    else:
        print("  FAIL - oversized key accepted")
        raise AssertionError(
            f"Oversized Idempotency-Key was accepted: "
            f"HTTP {response.status_code}"
        )

    
# ============================================================
# 9. RATE-LIMITING CHECK
# ============================================================

async def test_rate_limiting(client):
    print("\n" + "=" * 70)
    print("[9] RATE-LIMITING / LOGIN ABUSE")
    print("=" * 70)

    statuses = []

    for i in range(15):

        response = await client.post(
            LOGIN_ENDPOINT,
            data={
                "username":
                    "nonexistent-security-test@example.com",
                "password":
                    "DefinitelyWrongPassword123!",
            },
        )

        statuses.append(
            response.status_code
        )

    print(
        f"  Requests sent: {len(statuses)}"
    )

    print(
        f"  Statuses: {statuses}"
    )

    rate_limited = [
        status
        for status in statuses
        if status == 429
    ]

    if rate_limited:

        print(
            f"  PASS - rate limiting observed "
            f"({len(rate_limited)} responses with 429)"
        )

    else:

        print(
            "  WARN - no HTTP 429 observed"
        )

        print(
            "  Production recommendation: "
            "add login rate limiting / account lockout"
        )


# ============================================================
# 10. DEBUG / SERVER ERROR DISCLOSURE
# ============================================================

async def test_error_disclosure(client):
    print("\n" + "=" * 70)
    print("[10] ERROR RESPONSE DISCLOSURE")
    print("=" * 70)

    response = await client.get(
        "/api/v1/users/not-a-valid-uuid",
        headers=auth_headers(),
    )

    print(
        f"  HTTP {response.status_code}"
    )

    body = response.text

    print(
        f"  Response: {body[:500]}"
    )

    dangerous = [
        "Traceback",
        "File \"",
        "sqlalchemy",
        "asyncpg",
        "password_hash",
        "SECRET",
        "JWT_SECRET",
    ]

    found = [
        term
        for term in dangerous
        if term.lower() in body.lower()
    ]

    if found:

        print(
            f"  FAIL - internal details exposed: {found}"
        )

    else:

        print(
            "  PASS - no obvious stack-trace leakage"
        )


# ============================================================
# 11. OPENAPI / DOCS EXPOSURE
# ============================================================

async def test_docs_exposure(client):
    print("\n" + "=" * 70)
    print("[11] SWAGGER / OPENAPI EXPOSURE")
    print("=" * 70)

    docs = await client.get("/docs")

    openapi = await client.get(
        "/openapi.json"
    )

    print(
        f"  /docs       : HTTP {docs.status_code}"
    )

    print(
        f"  /openapi.json: HTTP {openapi.status_code}"
    )

    if docs.status_code == 200:
        print(
            "  WARN - Swagger UI publicly accessible"
        )
    else:
        print(
            "  PASS - Swagger UI not publicly accessible"
        )

    if openapi.status_code == 200:
        print(
            "  WARN - OpenAPI schema publicly accessible"
        )
    else:
        print(
            "  PASS - OpenAPI schema protected"
        )


# ============================================================
# MAIN
# ============================================================

async def main():

    print("=" * 70)
    print("BITNOVA PHASE 4.7 API ABUSE / PRODUCTION SECURITY TEST")
    print("=" * 70)

    print(
        f"API: {BASE_URL}"
    )

    if TOKEN:
        print(
            f"ACCESS_TOKEN: SET "
            f"(length={len(TOKEN)})"
        )
    else:
        print(
            "ACCESS_TOKEN: NOT SET"
        )

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=30,
    ) as client:

        await test_security_headers(client)

        await test_cors(client)

        await test_internal_endpoint_protection(
            client
        )

        await test_missing_auth_on_sensitive_endpoints(
            client
        )

        await test_http_method_abuse(client)

        await test_information_leakage(client)

        await test_malformed_json(client)

        if TOKEN:
            await test_oversized_idempotency_key(
                client
            )

        await test_rate_limiting(client)

        await test_error_disclosure(client)

        await test_docs_exposure(client)

    print("\n" + "=" * 70)
    print("PHASE 4.7 TEST EXECUTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())