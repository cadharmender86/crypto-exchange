from decimal import Decimal

from app.core.config import settings


class FxRateService:
    """Temporary abstraction for the active USDT/INR conversion rate.

    The persisted exchange-rate configuration will replace this environment
    fallback in the next migration step. Keeping the lookup behind a service
    prevents market consumers from depending directly on Settings.
    """

    @staticmethod
    def get_usdt_inr_rate() -> Decimal:
        return Decimal(str(settings.market_usdt_inr_rate))


fx_rate_service = FxRateService()
