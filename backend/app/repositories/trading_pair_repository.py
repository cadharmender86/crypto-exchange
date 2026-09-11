from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trading_pair import TradingPair


class TradingPairRepository:

    @staticmethod
    async def get_by_pair_code(
        db: AsyncSession,
        pair_code: str,
    ) -> TradingPair | None:

        result = await db.execute(
            select(TradingPair).where(
                TradingPair.pair_code == pair_code.upper()
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def list_active_pairs(
        db: AsyncSession,
    ) -> list[TradingPair]:

        result = await db.execute(
            select(TradingPair)
            .where(
                TradingPair.status == "ACTIVE",
                TradingPair.is_visible.is_(True),
            )
            .order_by(
                TradingPair.is_default.desc(),
                TradingPair.pair_code.asc(),
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def list_visible_pairs(
        db: AsyncSession,
    ) -> list[TradingPair]:

        result = await db.execute(
            select(TradingPair)
            .where(
                TradingPair.is_visible.is_(True)
            )
            .order_by(
                TradingPair.pair_code.asc(),
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def list_all_pairs(
        db: AsyncSession,
    ) -> list[TradingPair]:

        result = await db.execute(
            select(TradingPair)
            .order_by(
                TradingPair.pair_code.asc(),
            )
        )

        return list(result.scalars().all())

    @staticmethod
    async def get_default_pair(
        db: AsyncSession,
    ) -> TradingPair | None:

        result = await db.execute(
            select(TradingPair)
            .where(TradingPair.is_default.is_(True))
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def pair_exists(
        db: AsyncSession,
        pair_code: str,
    ) -> bool:

        pair = await TradingPairRepository.get_by_pair_code(
            db,
            pair_code,
        )

        return pair is not None