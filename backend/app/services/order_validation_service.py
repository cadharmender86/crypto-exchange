from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import TradingPairStatus
from app.core.exchange_errors import (
    InvalidOrderValueError,
    InvalidPriceError,
    InvalidQuantityError,
    MaintenanceModeError,
    SpotTradingDisabledError,
    TradingPairDisabledError,
    TradingPairNotFoundError,
)
from app.repositories.exchange_setting_repository import ExchangeSettingRepository
from app.repositories.trading_pair_repository import TradingPairRepository

class OrderValidationService:
    """
    Enterprise validation layer before an order reaches the matching engine.
    """

    @staticmethod
    async def validate_exchange_status(
        db: AsyncSession,
    ) -> None:

        maintenance = await ExchangeSettingRepository.get_by_key(
            db,
            "maintenance_mode",
        )

        if maintenance and maintenance.value.lower() == "true":
            raise MaintenanceModeError(
                "Exchange is currently under maintenance."
            )

        trading = await ExchangeSettingRepository.get_by_key(
            db,
            "spot_trading_enabled",
        )

        if trading and trading.value.lower() == "false":
            raise SpotTradingDisabledError(
                "Spot trading is disabled."
            )

    @staticmethod
    async def validate_trading_pair(
        db: AsyncSession,
        pair_code: str,
    ):

        pair = await TradingPairRepository.get_by_pair_code(
            db,
            pair_code.upper(),
        )

        if pair is None:
            raise TradingPairNotFoundError(
                f"Trading pair '{pair_code}' does not exist."
            )

        if pair.status != TradingPairStatus.ACTIVE:
            raise TradingPairDisabledError(
                f"{pair_code} is not active."
            )

        return pair

    @staticmethod
    def validate_price(
        pair,
        price: Decimal,
    ) -> None:

        decimals = abs(price.as_tuple().exponent)

        if decimals > pair.price_precision:
            raise InvalidPriceError(
                f"Price supports maximum "
                f"{pair.price_precision} decimal places."
            )

        tick = pair.tick_size

        if price % tick != Decimal("0"):
            raise InvalidPriceError(
                f"Price must be a multiple of tick size {tick}."
            )

    @staticmethod
    def validate_quantity(
        pair,
        quantity: Decimal,
    ) -> None:

        decimals = abs(quantity.as_tuple().exponent)

        if decimals > pair.quantity_precision:
            raise InvalidQuantityError(
                f"Quantity supports maximum "
                f"{pair.quantity_precision} decimal places."
            )

        if quantity % pair.step_size != Decimal("0"):
            raise InvalidQuantityError(
                f"Quantity must be multiple of {pair.step_size}."
            )

        if quantity < pair.min_order_quantity:
            raise InvalidQuantityError(
                f"Minimum quantity is {pair.min_order_quantity}."
            )

        if (
            pair.max_order_quantity
            and quantity > pair.max_order_quantity
        ):
            raise InvalidQuantityError(
                f"Maximum quantity is {pair.max_order_quantity}."
            )

    @staticmethod
    def validate_order_value(
        pair,
        *,
        quantity: Decimal,
        price: Decimal,
    ) -> Decimal:

        value = quantity * price

        if value < pair.min_order_value:
            raise InvalidOrderValueError(
                f"Minimum order value is "
                f"{pair.min_order_value}."
            )

        return value

    @staticmethod
    async def validate_limit_order(
        db: AsyncSession,
        *,
        pair_code: str,
        price: Decimal,
        quantity: Decimal,
    ):

        await OrderValidationService.validate_exchange_status(db)

        pair = await OrderValidationService.validate_trading_pair(
            db,
            pair_code,
        )

        OrderValidationService.validate_price(
            pair,
            price,
        )

        OrderValidationService.validate_quantity(
            pair,
            quantity,
        )

        order_value = (
            OrderValidationService.validate_order_value(
                pair,
                quantity=quantity,
                price=price,
            )
        )

        return pair, order_value