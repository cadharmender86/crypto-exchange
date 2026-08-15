from decimal import Decimal

import pytest

from app.services.withdrawal_service import WithdrawalService


def test_allowed_withdrawal_transitions():
    assert WithdrawalService.is_valid_transition("PENDING", "APPROVED")
    assert WithdrawalService.is_valid_transition("PENDING", "REJECTED")
    assert WithdrawalService.is_valid_transition("APPROVED", "PROCESSING")
    assert WithdrawalService.is_valid_transition("PROCESSING", "COMPLETED")
    assert WithdrawalService.is_valid_transition("PROCESSING", "FAILED")


def test_invalid_withdrawal_transitions():
    assert not WithdrawalService.is_valid_transition("REJECTED", "APPROVED")
    assert not WithdrawalService.is_valid_transition("COMPLETED", "REJECTED")
    assert not WithdrawalService.is_valid_transition("COMPLETED", "APPROVED")


def test_withdrawal_amount_must_be_positive():
    with pytest.raises(ValueError):
        WithdrawalService.validate_transition_amount(Decimal("0"))
    with pytest.raises(ValueError):
        WithdrawalService.validate_transition_amount(Decimal("-1"))
