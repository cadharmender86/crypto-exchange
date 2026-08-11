from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.core.config import settings
from app.schemas.internal import TestDepositRequest, TestDepositResponse
from app.services.test_deposit_service import TestDepositService


router = APIRouter(
    prefix="/internal",
    tags=["Internal / Development"],
)


@router.post(
    "/test-deposits",
    response_model=TestDepositResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_test_deposit(
    request: TestDepositRequest,
    x_internal_key: str = Header(..., alias="X-Internal-Key"),
    db: AsyncSession = Depends(get_db),
):
    """Credit development funds to a user's asset account.

    This endpoint is intentionally protected by a separate internal key and
    must never be exposed as a customer-facing deposit API.
    """
    if not settings.internal_test_deposit_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Test deposit endpoint is not configured",
        )

    if x_internal_key != settings.internal_test_deposit_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal key",
        )

    try:
        transaction, account = await TestDepositService.deposit(
            db,
            user_id=request.user_id,
            asset_id=request.asset_id,
            amount=request.amount,
            description=request.description,
        )
        await db.commit()

        return TestDepositResponse(
            transaction_id=transaction.id,
            reference=transaction.reference,
            status=transaction.status,
            user_id=request.user_id,
            asset_id=request.asset_id,
            amount=request.amount,
        )

    except ValueError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception:
        await db.rollback()
        raise
