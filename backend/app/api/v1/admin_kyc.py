from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.api.v1.admin_auth import require_permission
from app.models.admin import AdminUser, AuditLog
from app.models.kyc import KYCRecord, KYCStatus
from app.models.user import User
from app.schemas.kyc import KYCListResponse, KYCResponse, KYCReviewRequest


router = APIRouter(prefix="/admin/kyc", tags=["Admin KYC"])


def _response(record: KYCRecord, email: str) -> KYCResponse:
    return KYCResponse(
        id=record.id,
        user_id=record.user_id,
        user_email=email,
        status=record.status,
        document_type=record.document_type,
        document_reference=record.document_reference,
        submitted_at=record.submitted_at,
        reviewed_at=record.reviewed_at,
        reviewed_by_admin_id=record.reviewed_by_admin_id,
        rejection_reason=record.rejection_reason,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get("", response_model=KYCListResponse)
async def list_kyc(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    status_filter: KYCStatus | None = Query(None, alias="status"),
    search: str | None = Query(None, min_length=1, max_length=255),
    _: AdminUser = Depends(require_permission("KYC_READ")),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if status_filter is not None:
        filters.append(KYCRecord.status == status_filter.value)
    if search:
        filters.append(func.lower(User.email).like(f"%{search.strip().lower()}%"))

    base = select(KYCRecord).join(User, User.id == KYCRecord.user_id)
    count_result = await db.execute(
        select(func.count(KYCRecord.id)).select_from(KYCRecord).join(User, User.id == KYCRecord.user_id).where(*filters)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        base.where(*filters)
        .order_by(KYCRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    rows = result.all()
    return KYCListResponse(
        items=[_response(record, user.email) for record, user in rows],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{kyc_id}", response_model=KYCResponse)
async def get_kyc(
    kyc_id: UUID,
    _: AdminUser = Depends(require_permission("KYC_READ")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KYCRecord, User.email)
        .join(User, User.id == KYCRecord.user_id)
        .where(KYCRecord.id == kyc_id)
    )
    row = result.one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KYC record not found")
    record, email = row
    return _response(record, email)


async def _review(
    kyc_id: UUID,
    request: Request,
    payload: KYCReviewRequest,
    admin: AdminUser,
    db: AsyncSession,
    target_status: KYCStatus,
) -> KYCResponse:
    result = await db.execute(
        select(KYCRecord, User.email)
        .join(User, User.id == KYCRecord.user_id)
        .where(KYCRecord.id == kyc_id)
    )
    row = result.one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KYC record not found")

    record, email = row

    if record.status in {KYCStatus.APPROVED.value, KYCStatus.REJECTED.value}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"KYC record is already {record.status.lower()}",
        )

    old_status = record.status
    record.status = target_status.value
    record.reviewed_at = datetime.now(timezone.utc)
    record.reviewed_by_admin_id = admin.id
    record.rejection_reason = payload.reason if target_status == KYCStatus.REJECTED else None

    db.add(
        AuditLog(
            admin_user_id=admin.id,
            action=f"KYC_{target_status.value}",
            resource_type="KYC",
            resource_id=str(record.id),
            old_value={"status": old_status},
            new_value={"status": target_status.value},
            result="SUCCESS",
            reason=payload.reason,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    )

    await db.commit()
    await db.refresh(record)
    return _response(record, email)


@router.patch("/{kyc_id}/approve", response_model=KYCResponse)
async def approve_kyc(
    kyc_id: UUID,
    request: Request,
    payload: KYCReviewRequest,
    admin: AdminUser = Depends(require_permission("KYC_APPROVE")),
    db: AsyncSession = Depends(get_db),
):
    return await _review(kyc_id, request, payload, admin, db, KYCStatus.APPROVED)


@router.patch("/{kyc_id}/reject", response_model=KYCResponse)
async def reject_kyc(
    kyc_id: UUID,
    request: Request,
    payload: KYCReviewRequest,
    admin: AdminUser = Depends(require_permission("KYC_REJECT")),
    db: AsyncSession = Depends(get_db),
):
    return await _review(kyc_id, request, payload, admin, db, KYCStatus.REJECTED)


@router.patch("/{kyc_id}/under-review", response_model=KYCResponse)
async def mark_kyc_under_review(
    kyc_id: UUID,
    request: Request,
    payload: KYCReviewRequest,
    admin: AdminUser = Depends(require_permission("KYC_READ")),
    db: AsyncSession = Depends(get_db),
):
    return await _review(kyc_id, request, payload, admin, db, KYCStatus.UNDER_REVIEW)
