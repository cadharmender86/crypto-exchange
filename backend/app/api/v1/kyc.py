from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user
from app.schemas.kyc import (
    PersonalInfoRequest,
    PersonalInfoResponse,
)
from app.models.enums import DocumentType, KYCStatus, DocumentStatus
from app.services.kyc_service import KYCService, KYCDocumentService
from app.schemas.kyc_document import KYCUploadResponse
from app.models.kyc_document import KYCDocument
from app.models.kyc_profile import KYCProfile
# from app.services.kyc_service import KYCDocumentService
# from app.api.dependencies.auth import get_current_user

router = APIRouter()


@router.get(
    "/profile",
    response_model=PersonalInfoResponse,
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await KYCService.get_profile(
        db,
        current_user.id,
    )

    return profile


@router.put(
    "/personal-info",
    response_model=PersonalInfoResponse,
)
async def save_personal_info(
    payload: PersonalInfoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await KYCService.save_personal_info(
        db,
        current_user.id,
        payload,
    )

    return profile

@router.post(
    "/upload/pan",
    response_model=KYCUploadResponse,
)
async def upload_pan(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = await KYCDocumentService.upload_document(
        db=db,
        user=current_user,
        file=file,
        document_type=DocumentType.PAN,
    )

    return {
        "message": "PAN uploaded successfully.",
        "document": document,
    }

@router.post(
    "/upload/aadhaar-front",
    response_model=KYCUploadResponse,
)
async def upload_aadhaar_front(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = await KYCDocumentService.upload_document(
        db=db,
        user=current_user,
        file=file,
        document_type=DocumentType.AADHAAR_FRONT,
    )

    return {
        "message": "Aadhaar front uploaded successfully.",
        "document": document,
    }

@router.post(
    "/upload/aadhaar-back",
    response_model=KYCUploadResponse,
)
async def upload_aadhaar_back(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = await KYCDocumentService.upload_document(
        db=db,
        user=current_user,
        file=file,
        document_type=DocumentType.AADHAAR_BACK,
    )

    return {
        "message": "Aadhaar back uploaded successfully.",
        "document": document,
    }

@router.post(
    "/upload/selfie",
    response_model=KYCUploadResponse,
)
async def upload_selfie(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = await KYCDocumentService.upload_document(
        db=db,
        user=current_user,
        file=file,
        document_type=DocumentType.SELFIE,
    )

    return {
        "message": "Selfie uploaded successfully.",
        "document": document,
    }

@router.post("/submit")
async def submit_kyc(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get profile
    result = await db.execute(
        select(KYCProfile).where(
            KYCProfile.user_id == current_user.id
        )
    )

    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="KYC profile not found.",
        )

    # Validate personal information
    required_fields = [
        profile.first_name,
        profile.last_name,
        profile.date_of_birth,
        profile.nationality,
        profile.country,
        profile.state,
        profile.city,
        profile.address_line1,
        profile.postal_code,
    ]

    if any(field is None or field == "" for field in required_fields):
        raise HTTPException(
            status_code=400,
            detail="Complete personal information before submitting KYC.",
        )

    if profile.kyc_status in (
        KYCStatus.SUBMITTED,
        KYCStatus.UNDER_REVIEW,
        KYCStatus.APPROVED,
    ):
        raise HTTPException(
            status_code=400,
            detail="KYC has already been submitted.",
        )

    # Allow REJECTED users to resubmit after corrections.
    if profile.kyc_status == KYCStatus.REJECTED:
        profile.rejection_reason = None
        profile.verified_at = None
        profile.verified_by = None

    # Validate uploaded documents
    docs_result = await db.execute(
        select(KYCDocument.document_type).where(
            KYCDocument.user_id == current_user.id
        )
    )

    documents = {
        doc.document_type: doc
        for doc in docs_result.scalars().all()
    }

    required_documents = {
        DocumentType.PAN,
        DocumentType.AADHAAR_FRONT,
        DocumentType.AADHAAR_BACK,
        DocumentType.SELFIE,
    }

    missing = []
    rejected = []

    for doc_type in required_documents:
        doc = documents.get(doc_type)

        if doc is None:
            missing.append(doc_type.value)
        elif doc.status == DocumentStatus.REJECTED:
            rejected.append(doc_type.value)    

    if missing or rejected:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Complete all required KYC documents before submitting.",
                "missing_documents": missing,
                "rejected_documents": rejected,
            },
        )

    # Update profile status
    profile.kyc_status = KYCStatus.SUBMITTED
    profile.submitted_at = datetime.now(timezone.utc)

    # if profile.kyc_status == KYCStatus.NOT_STARTED:
    #     profile.kyc_status = KYCStatus.DRAFT

    await db.commit()
    await db.refresh(profile)

    return {
        "message": "KYC submitted successfully.",
        "status": profile.kyc_status.value,
        "submitted_at": profile.submitted_at,
    }