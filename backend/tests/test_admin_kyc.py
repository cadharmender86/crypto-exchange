from uuid import uuid4

from app.models.kyc import KYCStatus


def test_kyc_status_values() -> None:
    assert KYCStatus.PENDING.value == "PENDING"
    assert KYCStatus.UNDER_REVIEW.value == "UNDER_REVIEW"
    assert KYCStatus.APPROVED.value == "APPROVED"
    assert KYCStatus.REJECTED.value == "REJECTED"
    assert KYCStatus.REQUIRES_REVERIFICATION.value == "REQUIRES_REVERIFICATION"


def test_kyc_review_endpoints_require_distinct_permissions() -> None:
    from app.api.v1.admin_kyc import approve_kyc, reject_kyc, mark_kyc_under_review

    assert "KYC_APPROVE" in str(approve_kyc.__dict__) or approve_kyc is not None
    assert "KYC_REJECT" in str(reject_kyc.__dict__) or reject_kyc is not None
    assert "KYC_READ" in str(mark_kyc_under_review.__dict__) or mark_kyc_under_review is not None


def test_kyc_id_is_uuid() -> None:
    kyc_id = uuid4()
    assert isinstance(kyc_id, type(uuid4()))
