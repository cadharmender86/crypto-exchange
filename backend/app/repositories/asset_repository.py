from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset
from app.repositories.base_repository import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    model = Asset

    @classmethod
    async def get_by_symbol(
        cls,
        db: AsyncSession,
        symbol: str,
    ) -> Asset | None:

        result = await db.execute(
            select(Asset).where(
                Asset.symbol == symbol.upper()
            )
        )

        return result.scalar_one_or_none()

    @classmethod
    async def list_active_assets(
        cls,
        db: AsyncSession,
    ) -> list[Asset]:

        result = await db.execute(
            select(Asset)
            .where(Asset.is_active.is_(True))
            .order_by(Asset.symbol.asc())
        )

        return list(result.scalars().all())

    @classmethod
    async def list_tradable_assets(
        cls,
        db: AsyncSession,
    ) -> list[Asset]:

        result = await db.execute(
            select(Asset)
            .where(
                Asset.is_active.is_(True),
                Asset.trading_enabled.is_(True),
            )
            .order_by(Asset.symbol.asc())
        )

        return list(result.scalars().all())

    @classmethod
    async def list_deposit_assets(
        cls,
        db: AsyncSession,
    ) -> list[Asset]:

        result = await db.execute(
            select(Asset)
            .where(
                Asset.deposit_enabled.is_(True),
                Asset.is_active.is_(True),
            )
            .order_by(Asset.symbol.asc())
        )

        return list(result.scalars().all())

    @classmethod
    async def list_withdraw_assets(
        cls,
        db: AsyncSession,
    ) -> list[Asset]:

        result = await db.execute(
            select(Asset)
            .where(
                Asset.withdrawal_enabled.is_(True),
                Asset.is_active.is_(True),
            )
            .order_by(Asset.symbol.asc())
        )

        return list(result.scalars().all())