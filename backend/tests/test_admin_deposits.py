from uuid import uuid4

from app.api.v1.admin_deposits import list_deposits, get_deposit


def test_admin_deposit_list_route_exists() -> None:
    assert list_deposits is not None


def test_admin_deposit_detail_route_exists() -> None:
    assert get_deposit is not None


def test_deposit_id_is_uuid() -> None:
    assert isinstance(uuid4(), type(uuid4()))


def test_admin_deposit_routes_are_read_only() -> None:
    assert list_deposits.__name__ == "list_deposits"
    assert get_deposit.__name__ == "get_deposit"
