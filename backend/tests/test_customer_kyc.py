import pytest
from pydantic import ValidationError

from app.models.kyc import KYCStatus
from app.schemas.kyc import KYCSubmitRequest


def test_kyc_submit_request_accepts_valid_payload() -> None:
    payload = KYCSubmitRequest(
        document_type="PAN",
        document_reference="ABCDE1234F",
        extra_data={"name": "Test User"},
    )

    assert payload.document_type == "PAN"
    assert payload.document_reference == "ABCDE1234F"
    assert payload.extra_data == {"name": "Test User"}


def test_kyc_submit_request_rejects_short_document_type() -> None:
    with pytest.raises(ValidationError):
        KYCSubmitRequest(document_type="P", document_reference="ABC123")


def test_kyc_submit_request_rejects_short_document_reference() -> None:
    with pytest.raises(ValidationError):
        KYCSubmitRequest(document_type="PAN", document_reference="A")


def test_customer_kyc_lifecycle_statuses_are_supported() -> None:
    assert KYCStatus.PENDING.value == "PENDING"
    assert KYCStatus.UNDER_REVIEW.value == "UNDER_REVIEW"
    assert KYCStatus.APPROVED.value == "APPROVED"
    assert KYCStatus.REJECTED.value == "REJECTED"
    assert KYCStatus.REQUIRES_REVERIFICATION.value == "REQUIRES_REVERIFICATION"
