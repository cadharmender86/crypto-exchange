from decimal import Decimal

import pytest

from app.services.ledger_service import LedgerService


def test_balanced_entries_are_accepted(monkeypatch):
    class DummyDB:
        async def flush(self):
            return None

        def add(self, _):
            return None

    class DummyTransaction:
        id = "tx-1"

    monkeypatch.setattr(
        "app.services.ledger_service.LedgerTransaction",
        lambda **_: DummyTransaction(),
    )
    monkeypatch.setattr(
        "app.services.ledger_service.LedgerEntry",
        lambda **kwargs: kwargs,
    )
    monkeypatch.setattr(
        "app.services.ledger_service.uuid4",
        lambda: type("UUID", (), {"hex": "abcdef1234567890"})(),
    )

    transaction = __import__("asyncio").run(
        LedgerService.create_transaction(
            DummyDB(),
            transaction_type="TEST",
            entries=[
                {"account_id": "a", "entry_type": "DEBIT", "amount": Decimal("10")},
                {"account_id": "b", "entry_type": "CREDIT", "amount": Decimal("10")},
            ],
        )
    )
    assert transaction.id == "tx-1"


def test_unbalanced_entries_are_rejected():
    with pytest.raises(ValueError, match="Unbalanced ledger transaction"):
        __import__("asyncio").run(
            LedgerService.create_transaction(
                object(),
                transaction_type="TEST",
                entries=[
                    {"account_id": "a", "entry_type": "DEBIT", "amount": Decimal("10")},
                    {"account_id": "b", "entry_type": "CREDIT", "amount": Decimal("9")},
                ],
            )
        )


def test_negative_amount_is_rejected():
    with pytest.raises(ValueError, match="Ledger amount must be greater than zero"):
        __import__("asyncio").run(
            LedgerService.create_transaction(
                object(),
                transaction_type="TEST",
                entries=[
                    {"account_id": "a", "entry_type": "DEBIT", "amount": Decimal("-1")},
                    {"account_id": "b", "entry_type": "CREDIT", "amount": Decimal("1")},
                ],
            )
        )


def test_invalid_entry_type_is_rejected():
    with pytest.raises(ValueError, match="Invalid entry type"):
        __import__("asyncio").run(
            LedgerService.create_transaction(
                object(),
                transaction_type="TEST",
                entries=[
                    {"account_id": "a", "entry_type": "INVALID", "amount": Decimal("1")},
                    {"account_id": "b", "entry_type": "CREDIT", "amount": Decimal("1")},
                ],
            )
        )
