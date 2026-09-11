from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exchange_setting import ExchangeSetting


class ExchangeSettingRepository:

    @staticmethod
    async def get_by_key(
        db: AsyncSession,
        key: str,
    ) -> ExchangeSetting | None:

        result = await db.execute(
            select(ExchangeSetting).where(
                ExchangeSetting.key == key.lower()
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def list_all(
        db: AsyncSession,
    ) -> list[ExchangeSetting]:

        result = await db.execute(
            select(ExchangeSetting).order_by(
                ExchangeSetting.key.asc()
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def list_public_settings(
        db: AsyncSession,
    ) -> list[ExchangeSetting]:

        result = await db.execute(
            select(ExchangeSetting)
            .where(ExchangeSetting.is_public.is_(True))
            .order_by(ExchangeSetting.key.asc())
        )

        return list(result.scalars().all())

    @staticmethod
    async def exists(
        db: AsyncSession,
        key: str,
    ) -> bool:

        setting = await ExchangeSettingRepository.get_by_key(
            db,
            key,
        )

        return setting is not None

    @staticmethod
    async def create(
        db: AsyncSession,
        setting: ExchangeSetting,
    ) -> ExchangeSetting:

        db.add(setting)

        await db.flush()
        await db.refresh(setting)

        return setting

    @staticmethod
    async def update(
        db: AsyncSession,
        setting: ExchangeSetting,
    ) -> ExchangeSetting:

        await db.flush()
        await db.refresh(setting)

        return setting

    @staticmethod
    async def delete(
        db: AsyncSession,
        setting: ExchangeSetting,
    ) -> None:

        await db.delete(setting)
        await db.flush()