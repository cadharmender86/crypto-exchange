from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model = None

    @classmethod
    async def get_by_id(
        cls,
        db: AsyncSession,
        entity_id,
    ) -> ModelType | None:
        result = await db.execute(
            select(cls.model).where(
                cls.model.id == entity_id
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(
        cls,
        db: AsyncSession,
    ) -> list[ModelType]:
        result = await db.execute(select(cls.model))
        return list(result.scalars().all())

    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        entity: ModelType,
    ) -> ModelType:
        db.add(entity)
        await db.flush()
        await db.refresh(entity)
        return entity

    @classmethod
    async def delete(
        cls,
        db: AsyncSession,
        entity: ModelType,
    ) -> None:
        await db.delete(entity)
        await db.flush()