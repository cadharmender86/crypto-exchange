from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_user),
    # db: AsyncSession = Depends(get_db),
) -> UserResponse:

    # result = await db.execute(
    #     select(User).where(User.id == user_id)
    # )

    # user = result.scalar_one_or_none()

    # if user is None:
    #     raise HTTPException(
    #         status_code=404,
    #         detail="User not found",
    #     )

    return current_user