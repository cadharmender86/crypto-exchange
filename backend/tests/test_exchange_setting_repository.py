import asyncio

from app.core.database import AsyncSessionLocal
from app.repositories.exchange_setting_repository import ExchangeSettingRepository


async def main():
    async with AsyncSessionLocal() as db:
        setting = await ExchangeSettingRepository.get_by_key(
            db,
            "default_market",
        )

        print(setting.key, setting.value)

        settings = await ExchangeSettingRepository.list_public_settings(db)

        for item in settings:
            print(item.key, item.value)


if __name__ == "__main__":
    asyncio.run(main())