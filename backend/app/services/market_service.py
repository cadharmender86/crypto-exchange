from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.asset_repository import AssetRepository
from app.repositories.trading_pair_repository import TradingPairRepository
from app.repositories.exchange_setting_repository import ExchangeSettingRepository
from app.services.binance_market_service import binance_market_service


class MarketService:
    """
    Market orchestration service.

    Combines:
    - Database configuration
    - Trading pairs
    - Binance live market data
    """

    @staticmethod
    async def get_assets(db: AsyncSession):
        return await AssetRepository.list_active_assets(db)

    @staticmethod
    async def get_active_pairs(db: AsyncSession):
        return await TradingPairRepository.list_active_pairs(db)

    @staticmethod
    async def get_public_settings(
        db: AsyncSession,
    ) -> dict[str, str]:

        settings = await ExchangeSettingRepository.list_public_settings(db)

        return {
            setting.key: setting.value
            for setting in settings
        }

    @staticmethod
    async def get_market_overview(db: AsyncSession):

        default_market = await MarketService.get_default_market(db)

        pairs = await TradingPairRepository.list_active_pairs(db)

        tickers = binance_market_service.snapshot()

        ticker_map = {
            ticker["symbol"]: ticker
            for ticker in tickers
        }

        markets = []

        for pair in pairs:
            ticker = ticker_map.get(pair.pair_code)

            markets.append(
                {
                    "pair_code": pair.pair_code,
                    "display_name": pair.display_name,
                    "is_default": pair.is_default,
                    "price": ticker["lastPrice"] if ticker else None,
                    "change_percent": ticker["priceChangePercent"] if ticker else None,
                }
            )

        return {
            "default_market": default_market,
            "markets": markets,
        }