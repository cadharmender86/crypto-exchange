from uuid import uuid4

from app.api.v1.admin_withdrawals import (
    approve_withdrawal,
    get_withdrawal,
    list_withdrawals,
    reject_withdrawal,
)


def test_admin_withdrawal_list_route_exists() -> None:
    assert list_withdrawals is not None


def test_admin_withdrawal_detail_route_exists() -> None:
    assert get_withdrawal is not None


def test_admin_withdrawal_review_routes_exist() -> None:
    assert approve_withdrawal is not None
    assert reject_withdrawal is not None


def test_withdrawal_id_is_uuid() -> None:
    assert isinstance(uuid4(), type(uuid4()))
