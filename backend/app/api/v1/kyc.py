from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.models.kyc import KYCRecord, KYCStatus
from app.models.user import User
from app.schemas.kyc import KYCSubmitRequest, KYCUserResponse


router = APIRouter(prefix="/kyc", tags=["KYC"])



def _response(record: KYCRecord) -> KYCUserResponse:
    return KYCUserResponse(
        id=record.id,
        user_id=record.user_id,
        status=record.status,
        document_type=record.document_type,
        document_reference=record.document_reference,
        submitted_at=record.submitted_at,
        reviewed_at=record.reviewed_at,
        rejection_reason=record.rejection_reason,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


async def _get_user_kyc(db: AsyncSession, user_id):
    result = await db.execute(select(KYCRecord).where(KYCRecord.user_id == user_id))
    return result.scalar_one_or_none()


@router.get("", response_model=KYCUserResponse)
async def get_my_kyc(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KYCUserResponse:
    record = await _get_user_kyc(db, current_user.id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC record not found",
        )
    return _response(record)


@router.post("", response_model=KYCUserResponse, status_code=status.HTTP_201_CREATED)
async def submit_kyc(
    payload: KYCSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KYCUserResponse:
    record = await _get_user_kyc(db, current_user.id)

    if record is not None:
        if record.status in {
            KYCStatus.APPROVED.value,
            KYCStatus.UNDER_REVIEW.value,
        }:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"KYC record is already {record.status.lower()}",
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="KYC record already exists; use PATCH /api/v1/kyc to resubmit",
        )

    now = datetime.now(timezone.utc)
    record = KYCRecord(
        user_id=current_user.id,
        status=KYCStatus.PENDING.value,
        document_type=payload.document_type,
        document_reference=payload.document_reference,
        submitted_at=now,
        extra_data=payload.extra_data,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return _response(record)


@router.patch("", response_model=KYCUserResponse)
async def resubmit_kyc(
    payload: KYCSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> KYCUserResponse:
    record = await _get_user_kyc(db, current_user.id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC record not found; submit KYC first",
        )

    if record.status in {
        KYCStatus.APPROVED.value,
        KYCStatus.UNDER_REVIEW.value,
    }:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"KYC record is already {record.status.lower()}",
        )

    record.status = KYCStatus.PENDING.value
    record.document_type = payload.document_type
    record.document_reference = payload.document_reference
    record.submitted_at = datetime.now(timezone.utc)
    record.reviewed_at = None
    record.reviewed_by_admin_id = None
    record.rejection_reason = None
    record.extra_data = payload.extra_data

    await db.commit()
    await db.refresh(record)
    return _response(record)
