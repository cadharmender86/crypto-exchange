from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetResponse


router = APIRouter(
    prefix="/assets",
    tags=["Assets"],
)


@router.get(
    "",
    response_model=list[AssetResponse],
)
async def get_assets(
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(Asset).where(Asset.is_active.is_(True))
        .order_by(Asset.symbol)
    )

    return list(result.scalars().all())