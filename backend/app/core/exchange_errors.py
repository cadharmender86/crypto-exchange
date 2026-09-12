class ExchangeError(Exception):
    """Base class for exchange exceptions."""


class MaintenanceModeError(ExchangeError):
    pass


class SpotTradingDisabledError(ExchangeError):
    pass


class TradingPairNotFoundError(ExchangeError):
    pass


class TradingPairDisabledError(ExchangeError):
    pass


class InvalidPriceError(ExchangeError):
    pass


class InvalidQuantityError(ExchangeError):
    pass


class InvalidOrderValueError(ExchangeError):
    pass


class InsufficientBalanceError(ExchangeError):
    pass