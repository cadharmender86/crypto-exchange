from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1.admin_auth import decode_admin_token, require_permission
from app.api.v1.auth import create_access_token


def test_customer_access_token_is_rejected_as_admin_token():
    token = create_access_token(uuid4())

    with pytest.raises(HTTPException) as exc:
        decode_admin_token(token)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_permission_dependency_rejects_missing_permission():
    dependency = require_permission("USER_READ")

    class Admin:
        pass

    with pytest.raises(HTTPException) as exc:
        await dependency(Admin(), set())

    assert exc.value.status_code == 403
    assert exc.value.detail == "Insufficient admin permissions"
