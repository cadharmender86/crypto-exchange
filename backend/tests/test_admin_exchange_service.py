import asyncio

from app.core.database import AsyncSessionLocal
from app.services.admin_exchange_service import AdminExchangeService


async def main():
    async with AsyncSessionLocal() as db:

        print("Exchange Settings")
        settings = await AdminExchangeService.list_settings(db)

        for setting in settings:
            print(setting.key, setting.value)

        print("\nTrading Pairs")
        pairs = await AdminExchangeService.list_active_trading_pairs(db)

        for pair in pairs:
            print(pair.pair_code, pair.display_name)

        default_pair = await AdminExchangeService.get_trading_pair(
            db,
            "BTCUSDT",
        )

        print("\nDefault Pair")
        print(default_pair.pair_code, default_pair.display_name)


if __name__ == "__main__":
    asyncio.run(main())