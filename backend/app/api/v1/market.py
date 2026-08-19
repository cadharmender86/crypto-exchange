from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.binance_market_service import binance_market_service

router = APIRouter(prefix="/market", tags=["Market"])


@router.get("/tickers")
async def get_market_tickers():
    return binance_market_service.snapshot()


@router.websocket("/ws")
async def market_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        async for ticker in binance_market_service.subscribe():
            await websocket.send_json(ticker)
    except WebSocketDisconnect:
        return
