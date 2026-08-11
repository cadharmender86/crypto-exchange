import hashlib
import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idempotency import IdempotencyRecord


class IdempotencyService:

    @staticmethod
    def hash_request(data: dict) -> str:

        normalized = json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )

        return hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

    @staticmethod
    async def get_record(
        db: AsyncSession,
        *,
        user_id: UUID,
        idempotency_key: str,
    ) -> IdempotencyRecord | None:

        result = await db.execute(
            select(IdempotencyRecord)
            .where(
                IdempotencyRecord.user_id == user_id,
                IdempotencyRecord.idempotency_key
                == idempotency_key,
            )
        )

        return result.scalar_one_or_none()