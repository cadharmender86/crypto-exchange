from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.asset import Asset
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from app.services.binance_market_service import binance_market_service

router = APIRouter(prefix="/market", tags=["Market"])


@router.get("/assets")
async def get_market_assets():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Asset)
            .where(Asset.is_active.is_(True))
            .order_by(Asset.symbol)
        )

        assets = result.scalars().all()

        return [
            {
                "id": str(asset.id),
                "symbol": asset.symbol,
                "name": asset.name,
                "asset_type": asset.asset_type,
                "decimal_places": asset.decimal_places,
                "is_active": asset.is_active,
                "deposit_enabled": asset.deposit_enabled,
                "withdrawal_enabled": asset.withdrawal_enabled,
                "trading_enabled": asset.trading_enabled,
                "is_fiat": asset.asset_type == "FIAT",
            }
            for asset in assets
        ]
    
@router.get("/tickers")
async def get_market_tickers():
    return binance_market_service.snapshot()


@router.get("/candles")
async def get_market_candles(symbol: str = "BTCUSDT", interval: str = "1m", limit: int = 200):
    try:
        return await binance_market_service.history_candles(symbol, interval, limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Unable to load market candles") from exc


@router.websocket("/ws")
async def market_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        async for ticker in binance_market_service.subscribe():
            await websocket.send_json(ticker)
    except WebSocketDisconnect:
        return


@router.websocket("/ws/candles/{symbol}/{interval}")
async def candle_websocket(websocket: WebSocket, symbol: str, interval: str):
    try:
        binance_market_service.normalize_symbol(symbol)
        binance_market_service.normalize_interval(interval)
    except ValueError as exc:
        await websocket.close(code=1008, reason=str(exc))
        return

    await websocket.accept()
    try:
        async for candle in binance_market_service.subscribe_candles(symbol, interval):
            await websocket.send_json(candle)
    except WebSocketDisconnect:
        return
