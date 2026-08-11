from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.transfer import (
    TransferRequest,
    TransferResponse,
)
from app.services.transfer_service import (
    TransferService,
)

# CHANGE THIS IMPORT TO YOUR EXISTING AUTH DEPENDENCY
from app.api.dependencies import get_current_user


router = APIRouter(
    prefix="/transfers",
    tags=["Transfers"],
)


@router.post(
    "",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transfer(
    request: TransferRequest,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=8,
        max_length=100,
    ),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    try:

        transaction = (
            await TransferService.transfer(
                db,
                from_user_id=current_user.id,
                to_user_id=request.to_user_id,
                asset_id=request.asset_id,
                amount=request.amount,
                idempotency_key=idempotency_key,
                description=request.description,
            )
        )

        return TransferResponse(
            transaction_id=transaction.id,
            reference=transaction.reference,
            status=transaction.status,
        )

    except ValueError as exc:

        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )