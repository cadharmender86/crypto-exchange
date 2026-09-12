from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.asset_repository import AssetRepository
from app.repositories.exchange_setting_repository import ExchangeSettingRepository
from app.repositories.trading_pair_repository import TradingPairRepository
from app.models.exchange_setting import ExchangeSetting
from app.models.trading_pair import TradingPair
from app.core.constants import SettingValueType


class AdminExchangeService:
    """
    Business layer for BitNova Exchange Configuration.
    """

    # ---------------------------------------------------
    # Exchange Settings
    # ---------------------------------------------------

    @staticmethod
    async def list_settings(
        db: AsyncSession,
    ) -> list[ExchangeSetting]:

        return await ExchangeSettingRepository.list_settings(db)

    @staticmethod
    async def get_setting(
        db: AsyncSession,
        key: str,
    ) -> ExchangeSetting | None:
        return await ExchangeSettingRepository.get_by_key(db, key)

    @staticmethod
    async def update_setting(
        db: AsyncSession,
        *,
        key: str,
        value: str,
    ) -> ExchangeSetting:

        setting = await ExchangeSettingRepository.get_by_key(db, key)

        if setting is None:
            raise ValueError("Exchange setting not found.")

        # Validate value according to stored type.
        AdminExchangeService._validate_setting_value(
            setting.value_type,
            value,
        )

        return await ExchangeSettingRepository.update_value(
            db=db,
            key=key,
            value=value,
        )

    # ---------------------------------------------------
    # Trading Pair Management
    # ---------------------------------------------------

    @staticmethod
    async def list_trading_pairs(
        db: AsyncSession,
    ) -> list[TradingPair]:
        return await TradingPairRepository.list_all(db)

    @staticmethod
    async def list_active_trading_pairs(
        db: AsyncSession,
    ) -> list[TradingPair]:
        return await TradingPairRepository.list_active_pairs(db)

    @staticmethod
    async def get_trading_pair(
        db: AsyncSession,
        pair_code: str,
    ) -> TradingPair | None:
        return await TradingPairRepository.get_by_pair_code(
            db,
            pair_code,
        )

    @staticmethod
    async def create_trading_pair(
        db: AsyncSession,
        *,
        base_symbol: str,
        quote_symbol: str,
        display_name: str,
        price_precision: int,
        quantity_precision: int,
        tick_size: Decimal,
        step_size: Decimal,
        min_order_quantity: Decimal,
        max_order_quantity: Decimal | None,
        min_order_value: Decimal,
    ) -> TradingPair:

        base_asset = await AssetRepository.get_by_symbol(db, base_symbol)
        quote_asset = await AssetRepository.get_by_symbol(db, quote_symbol)

        if base_asset is None:
            raise ValueError(f"Asset '{base_symbol}' does not exist.")

        if quote_asset is None:
            raise ValueError(f"Asset '{quote_symbol}' does not exist.")

        if base_asset.symbol == quote_asset.symbol:
            raise ValueError("Base and quote asset cannot be identical.")

        pair_code = f"{base_asset.symbol}{quote_asset.symbol}"

        existing = await TradingPairRepository.get_by_pair_code(
            db,
            pair_code,
        )

        if existing:
            raise ValueError("Trading pair already exists.")

        return await TradingPairRepository.create(
            db=db,
            base_asset_id=base_asset.id,
            quote_asset_id=quote_asset.id,
            pair_code=pair_code,
            display_name=display_name,
            price_precision=price_precision,
            quantity_precision=quantity_precision,
            tick_size=tick_size,
            step_size=step_size,
            min_order_quantity=min_order_quantity,
            max_order_quantity=max_order_quantity,
            min_order_value=min_order_value,
        )

    @staticmethod
    async def set_default_trading_pair(
        db: AsyncSession,
        pair_code: str,
    ) -> TradingPair:

        pair = await TradingPairRepository.get_by_pair_code(
            db,
            pair_code,
        )

        if pair is None:
            raise ValueError("Trading pair not found.")

        await TradingPairRepository.clear_default_pair(db)

        updated_pair = await TradingPairRepository.set_default_pair(
            db,
            pair.id,
        )

        await ExchangeSettingRepository.update_value(
            db=db,
            key="default_market",
            value=pair_code.upper(),
        )

        return updated_pair

    @staticmethod
    async def change_pair_status(
        db: AsyncSession,
        *,
        pair_code: str,
        status: str,
    ) -> TradingPair:

        pair = await TradingPairRepository.get_by_pair_code(
            db,
            pair_code,
        )

        if pair is None:
            raise ValueError("Trading pair not found.")

        return await TradingPairRepository.update_status(
            db=db,
            pair_id=pair.id,
            status=status.upper(),
        )

    # ---------------------------------------------------
    # Validation Helpers
    # ---------------------------------------------------

    @staticmethod
    def _validate_setting_value(
        value_type: str,
        value: str,
    ) -> None:

        if value_type == SettingValueType.BOOLEAN:
            if value.lower() not in {
                "true",
                "false",
            }:
                raise ValueError("Boolean value must be true or false.")

        elif value_type == SettingValueType.INTEGER:
            int(value)

        elif value_type == SettingValueType.DECIMAL:
            Decimal(value)

        elif value_type == SettingValueType.JSON:
            import json

            json.loads(value)

        elif value_type == SettingValueType.STRING:
            return

        else:
            raise ValueError("Unsupported setting value type.")