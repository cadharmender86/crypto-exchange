# from sqlalchemy import select
from app.core.database import AsyncSessionLocal
# from app.models.asset import Asset
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from app.services.binance_market_service import binance_market_service
from app.services.market_service import MarketService
from app.repositories.exchange_setting_repository import ExchangeSettingRepository

router = APIRouter(prefix="/market", tags=["Market"])


@router.get("/assets")
async def get_market_assets():
    async with AsyncSessionLocal() as db:
        assets = await MarketService.get_assets(db)

        return [
            {
                "id": str(asset.id),
                "symbol": asset.symbol,
                "name": asset.name,
                "asset_type": asset.asset_type,
                "decimal_places": asset.decimal_places,
                "deposit_enabled": asset.deposit_enabled,
                "withdrawal_enabled": asset.withdrawal_enabled,
                "trading_enabled": asset.trading_enabled,
                "is_fiat": asset.asset_type == "FIAT",
            }
            for asset in assets
        ]

@router.get("/pairs")
async def get_market_pairs():
    async with AsyncSessionLocal() as db:
        pairs = await MarketService.get_active_pairs(db)

        return [
            {
                "id": str(pair.id),
                "pair_code": pair.pair_code,
                "display_name": pair.display_name,
                "base_asset": pair.base_asset.symbol,
                "quote_asset": pair.quote_asset.symbol,
                "price_precision": pair.price_precision,
                "quantity_precision": pair.quantity_precision,
                "tick_size": str(pair.tick_size),
                "step_size": str(pair.step_size),
                "min_order_quantity": str(pair.min_order_quantity),
                "max_order_quantity": (
                    str(pair.max_order_quantity)
                    if pair.max_order_quantity
                    else None
                ),
                "min_order_value": str(pair.min_order_value),
                "is_default": pair.is_default,
                "status": pair.status,
            }
            for pair in pairs
        ]


@router.get("/default-market")
async def get_default_market():
    async with AsyncSessionLocal() as db:

        symbol = await MarketService.get_default_market(db)

        return {"default_market": symbol}


@router.get("/tickers")
async def get_market_tickers():
    return binance_market_service.snapshot()


@router.get("/candles")
async def get_market_candles(
    symbol: str | None = None,
    interval: str = "1m",
    limit: int = 200,
):
    async with AsyncSessionLocal() as db:

        if symbol is None:
            symbol = await MarketService.get_default_market(db)

    try:
        return await binance_market_service.history_candles(
            symbol,
            interval,
            limit,
        )

    except ValueError as exc:
        raise HTTPException(400, detail=str(exc))

    except Exception:
        raise HTTPException(
            502,
            detail="Unable to load market candles",
        )


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

@router.get("/settings/public")
async def get_public_market_settings():

    async with AsyncSessionLocal() as db:

        settings = await ExchangeSettingRepository.list_public_settings(db)

        return {
            setting.key: setting.value
            for setting in settings
        }    