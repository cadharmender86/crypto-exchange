from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.api.v1.orders import cancel_order, create_order
from app.schemas.order import CreateOrderRequest


def test_order_routes_exist() -> None:
    assert create_order is not None
    assert cancel_order is not None


def test_limit_order_request_accepts_valid_payload() -> None:
    request = CreateOrderRequest(
        base_asset_id=uuid4(),
        quote_asset_id=uuid4(),
        side="BUY",
        order_type="LIMIT",
        price=Decimal("100.25"),
        quantity=Decimal("0.50"),
        client_order_id="client-001",
    )

    assert request.side == "BUY"
    assert request.order_type == "LIMIT"
    assert request.price == Decimal("100.25")
    assert request.quantity == Decimal("0.50")


def test_order_request_rejects_market_order_for_current_phase() -> None:
    with pytest.raises(ValidationError):
        CreateOrderRequest(
            base_asset_id=uuid4(),
            quote_asset_id=uuid4(),
            side="BUY",
            order_type="MARKET",
            price=Decimal("100"),
            quantity=Decimal("1"),
        )


def test_order_request_rejects_invalid_side() -> None:
    with pytest.raises(ValidationError):
        CreateOrderRequest(
            base_asset_id=uuid4(),
            quote_asset_id=uuid4(),
            side="HOLD",
            order_type="LIMIT",
            price=Decimal("100"),
            quantity=Decimal("1"),
        )


def test_order_request_requires_positive_price_and_quantity() -> None:
    with pytest.raises(ValidationError):
        CreateOrderRequest(
            base_asset_id=uuid4(),
            quote_asset_id=uuid4(),
            side="BUY",
            order_type="LIMIT",
            price=Decimal("0"),
            quantity=Decimal("1"),
        )

    with pytest.raises(ValidationError):
        CreateOrderRequest(
            base_asset_id=uuid4(),
            quote_asset_id=uuid4(),
            side="SELL",
            order_type="LIMIT",
            price=Decimal("100"),
            quantity=Decimal("0"),
        )
