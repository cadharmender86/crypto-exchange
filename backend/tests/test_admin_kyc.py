import pytest
from fastapi import HTTPException

from app.api.v1.admin_auth import require_permission
from app.models.kyc import KYCStatus


class DummyAdmin:
    id = "admin-test"


@pytest.mark.asyncio
async def test_kyc_approve_requires_kyc_approve_permission() -> None:
    dependency = require_permission("KYC_APPROVE")

    assert await dependency(DummyAdmin(), {"KYC_APPROVE"}) is not None

    with pytest.raises(HTTPException) as exc_info:
        await dependency(DummyAdmin(), {"KYC_READ"})

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient admin permissions"


@pytest.mark.asyncio
async def test_kyc_reject_requires_kyc_reject_permission() -> None:
    dependency = require_permission("KYC_REJECT")

    assert await dependency(DummyAdmin(), {"KYC_REJECT"}) is not None

    with pytest.raises(HTTPException) as exc_info:
        await dependency(DummyAdmin(), {"KYC_READ"})

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_kyc_read_permission_does_not_grant_approval() -> None:
    dependency = require_permission("KYC_APPROVE")

    with pytest.raises(HTTPException) as exc_info:
        await dependency(DummyAdmin(), {"KYC_READ"})

    assert exc_info.value.status_code == 403


def test_kyc_status_values() -> None:
    assert [status.value for status in KYCStatus] == [
        "PENDING",
        "UNDER_REVIEW",
        "APPROVED",
        "REJECTED",
        "REQUIRES_REVERIFICATION",
    ]
