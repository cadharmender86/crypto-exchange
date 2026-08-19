from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.trade import TradeHistoryResponse
from app.services.trade_service import TradeService


router = APIRouter(prefix="/trades", tags=["Trades"])


@router.get("/history", response_model=list[TradeHistoryResponse])
async def get_trade_history(
    symbol: str | None = Query(default=None, min_length=1, max_length=30),
    side: str | None = Query(default=None, pattern="^(BUY|SELL)$"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TradeService.list_history(
        db,
        user_id=current_user.id,
        symbol=symbol,
        side=side,
        limit=limit,
        offset=offset,
    )
