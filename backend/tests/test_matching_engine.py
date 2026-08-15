from decimal import Decimal

from app.services.matching_engine import MatchingEngine


def test_matching_engine_is_available() -> None:
    assert MatchingEngine.match_order is not None


def test_weighted_average_for_partial_fills() -> None:
    class OrderStub:
        filled_quantity = Decimal("2")
        average_execution_price = Decimal("100")

    average = MatchingEngine._weighted_average(
        OrderStub(), Decimal("110"), Decimal("1")
    )

    assert average == Decimal("103.3333333333333333333333333")
