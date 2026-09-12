from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal


from app.core.database import get_db

from app.services.admin_exchange_service import AdminExchangeService

from app.schemas.admin_exchange import (
    ExchangeSettingResponse,
    UpdateExchangeSettingRequest,
    TradingPairResponse,
    CreateTradingPairRequest,
    UpdateTradingPairStatusRequest,
)

router = APIRouter(
    prefix="/admin/exchange",
    tags=["Admin Exchange"],
)

@router.get("/ping")
async def admin_exchange_ping():
    print("PING ENDPOINT HIT")
    return {"status": "ok"}

@router.get(
    "/settings",
    response_model=list[ExchangeSettingResponse],
)
async def list_exchange_settings(
    db: AsyncSession = Depends(get_db),
):
    settings = await AdminExchangeService.list_settings(db)

    return [
        ExchangeSettingResponse.model_validate(setting)
        for setting in settings
    ]


@router.patch(
    "/settings/{key}",
    response_model=ExchangeSettingResponse,
)
async def update_exchange_setting(
    key: str,
    payload: UpdateExchangeSettingRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await AdminExchangeService.update_setting(
            db,
            key=key,
            value=payload.value,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

def serialize_pair(pair):
    return TradingPairResponse(
        id=str(pair.id),
        pair_code=pair.pair_code,
        display_name=pair.display_name,

        base_asset=pair.base_asset.symbol,
        quote_asset=pair.quote_asset.symbol,

        price_precision=pair.price_precision,
        quantity_precision=pair.quantity_precision,

        tick_size=pair.tick_size,
        step_size=pair.step_size,

        min_order_quantity=pair.min_order_quantity,
        max_order_quantity=pair.max_order_quantity,
        min_order_value=pair.min_order_value,

        status=pair.status,
        is_visible=pair.is_visible,
        is_default=pair.is_default,
    )


@router.get(
    "/pairs",
    response_model=list[TradingPairResponse],
)
async def list_trading_pairs(
    db: AsyncSession = Depends(get_db),
):
    pairs = await AdminExchangeService.list_trading_pairs(db)

    return [serialize_pair(pair) for pair in pairs]


@router.post(
    "/pairs",
    response_model=TradingPairResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_trading_pair(
    payload: CreateTradingPairRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        pair = await AdminExchangeService.create_trading_pair(
            db=db,
            base_symbol=payload.base_symbol,
            quote_symbol=payload.quote_symbol,
            display_name=payload.display_name,
            price_precision=payload.price_precision,
            quantity_precision=payload.quantity_precision,
            tick_size=payload.tick_size,
            step_size=payload.step_size,
            min_order_quantity=payload.min_order_quantity,
            max_order_quantity=payload.max_order_quantity,
            min_order_value=payload.min_order_value,
        )

        return serialize_pair(pair)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

@router.patch(
    "/pairs/{pair_code}/status",
    response_model=TradingPairResponse,
)
async def update_pair_status(
    pair_code: str,
    payload: UpdateTradingPairStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        pair = await AdminExchangeService.change_pair_status(
            db=db,
            pair_code=pair_code,
            status=payload.status,
        )

        return serialize_pair(pair)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

@router.patch(
    "/pairs/{pair_code}/default",
    response_model=TradingPairResponse,
)
async def set_default_trading_pair(
    pair_code: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        pair = await AdminExchangeService.set_default_trading_pair(
            db,
            pair_code,
        )

        return serialize_pair(pair)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )        