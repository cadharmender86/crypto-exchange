from uuid import uuid4

from app.api.v1.admin_auth import (
    create_admin_access_token,
    create_admin_refresh_token,
    decode_admin_token,
)
from app.api.v1.auth import hash_password, verify_password


def test_admin_password_hash_round_trip() -> None:
    password = "StrongTestPassword!123"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_admin_access_token_has_admin_type() -> None:
    admin_id = uuid4()
    token = create_admin_access_token(admin_id)
    payload = decode_admin_token(token)

    assert payload["sub"] == str(admin_id)
    assert payload["type"] == "admin_access"
    assert "exp" in payload


def test_admin_refresh_token_cannot_be_used_as_access_token() -> None:
    admin_id = uuid4()
    refresh_token = create_admin_refresh_token(admin_id)

    try:
        decode_admin_token(refresh_token)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 401
    else:
        raise AssertionError("Admin refresh token was accepted as an access token")
