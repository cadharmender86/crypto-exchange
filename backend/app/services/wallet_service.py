from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet


class WalletService:

    @staticmethod
    async def create_wallet(
        db: AsyncSession,
        user_id: UUID,
        wallet_type: str = "CUSTOMER",
    ) -> Wallet:

        wallet_type = wallet_type.strip().upper()

        if not wallet_type:
            raise ValueError(
                "Wallet type is required"
            )

        existing = await db.execute(
            select(Wallet).where(
                Wallet.user_id == user_id,
                Wallet.wallet_type == wallet_type,
            )
        )

        wallet = existing.scalar_one_or_none()

        if wallet:
            raise ValueError(
                "Wallet already exists"
            )

        wallet = Wallet(
            user_id=user_id,
            wallet_type=wallet_type,
            status="ACTIVE",
        )

        db.add(wallet)

        try:
            await db.flush()

        except IntegrityError:
            await db.rollback()

            raise ValueError(
                "Wallet already exists"
            )

        await db.refresh(wallet)

        return wallet

    @staticmethod
    async def get_wallet(
        db: AsyncSession,
        wallet_id: UUID,
    ) -> Wallet | None:

        result = await db.execute(
            select(Wallet).where(
                Wallet.id == wallet_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_wallet(
        db: AsyncSession,
        user_id: UUID,
        wallet_type: str = "CUSTOMER",
    ) -> Wallet | None:

        wallet_type = wallet_type.strip().upper()

        result = await db.execute(
            select(Wallet).where(
                Wallet.user_id == user_id,
                Wallet.wallet_type == wallet_type,
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def list_user_wallets(
        db: AsyncSession,
        user_id: UUID,
    ) -> list[Wallet]:

        result = await db.execute(
            select(Wallet)
            .where(
                Wallet.user_id == user_id
            )
            .order_by(Wallet.created_at)
        )

        return list(result.scalars().all())