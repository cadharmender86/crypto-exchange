from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.trading_pair_repository import TradingPairRepository
from app.services.exchange_setting_service import ExchangeSettingService


class TradingPairService:

    @staticmethod
    async def list_markets(
        db: AsyncSession,
    ) -> list[dict]:

        pairs = await TradingPairRepository.list_active_pairs(db)

        return [
            {
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
                "status": pair.status,
                "is_default": pair.is_default,
            }
            for pair in pairs
        ]

    @staticmethod
    async def get_market(
        db: AsyncSession,
        pair_code: str,
    ) -> dict:

        pair = await TradingPairRepository.get_by_pair_code(
            db,
            pair_code,
        )

        if pair is None:
            raise ValueError("Trading pair not found.")

        return {
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
            "status": pair.status,
            "is_default": pair.is_default,
        }

    @staticmethod
    async def get_default_market(
        db: AsyncSession,
    ) -> dict:

        default_market = await ExchangeSettingService.get_string(
            db,
            "default_market",
        )

        pair = await TradingPairRepository.get_by_pair_code(
            db,
            default_market,
        )

        if pair is None:
            raise ValueError("Default market configuration is invalid.")

        return {
            "pair_code": pair.pair_code,
            "display_name": pair.display_name,
            "base_asset": pair.base_asset.symbol,
            "quote_asset": pair.quote_asset.symbol,
            "is_default": True,
        }