from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api.v1.admin_rbac import require_super_admin
from app.schemas.admin_rbac import AdminCreateRequest


def test_admin_create_request_requires_strong_initial_password() -> None:
    payload = AdminCreateRequest(
        email="staff@example.com",
        full_name="Staff Admin",
        password="StrongPassword!123",
        role_id=uuid4(),
        reason="Create operations staff account",
    )

    assert payload.email == "staff@example.com"
    assert payload.role_id is not None


def test_admin_create_request_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        AdminCreateRequest(
            email="staff@example.com",
            full_name="Staff Admin",
            password="short",
            role_id=uuid4(),
            reason="Create staff account",
        )


@pytest.mark.asyncio
async def test_non_super_admin_cannot_create_admin() -> None:
    class FakeResult:
        def scalar_one_or_none(self):
            return None

    class FakeDb:
        async def execute(self, _query):
            return FakeResult()

    class Admin:
        id = uuid4()

    with pytest.raises(HTTPException) as exc:
        await require_super_admin(Admin(), FakeDb())

    assert exc.value.status_code == 403
    assert exc.value.detail == "Only SUPER_ADMIN can manage administrator accounts"
