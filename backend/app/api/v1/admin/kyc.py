from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.kyc_document import KYCDocument
from app.schemas.admin_kyc import AdminKYCQueueItem
from app.services.admin_kyc_service import AdminKYCService
from app.schemas.admin_kyc_detail import AdminKYCDetailResponse
from app.schemas.admin_kyc_action import ApproveKYCResponse

router = APIRouter(prefix="/kyc", tags=["Admin KYC"])


@router.get(
    "/queue",
    response_model=list[AdminKYCQueueItem],
)
async def kyc_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await AdminKYCService.get_queue(db)

@router.get(
    "/{user_id}",
    response_model=AdminKYCDetailResponse,
)
async def get_kyc_detail(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    detail = await AdminKYCService.get_kyc_detail(db, user_id)

    if detail is None:
        raise HTTPException(
            status_code=404,
            detail="KYC application not found.",
        )

    return detail

@router.get("/document/{document_id}")
async def get_kyc_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(KYCDocument).where(
            KYCDocument.id == document_id
        )
    )

    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    file_path = Path("/app") / document.storage_path

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document file not found.",
        )

    return FileResponse(
        path=file_path,
        media_type=document.mime_type,
        filename=document.file_name,
    )

@router.post(
    "/{user_id}/approve",
    response_model=ApproveKYCResponse,
)
async def approve_kyc(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        profile = await AdminKYCService.approve_kyc(
            db=db,
            user_id=user_id,
            admin_user=current_user,
        )

        if profile is None:
            raise HTTPException(
                status_code=404,
                detail="KYC application not found.",
            )

        return {
            "message": "KYC approved successfully.",
            "status": profile.kyc_status.value,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )