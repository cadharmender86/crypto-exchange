import json
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.idempotency import IdempotencyRecord
from app.services.balance_service import BalanceService
from app.services.idempotency_service import IdempotencyService
from app.services.ledger_service import LedgerService


class TransferService:

    @staticmethod
    async def transfer(
        db: AsyncSession,
        *,
        from_user_id: UUID,
        to_user_id: UUID,
        asset_id: UUID,
        amount: Decimal,
        idempotency_key: str,
        description: str | None = None,
    ):

        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError(
                "Transfer amount must be greater than zero"
            )

        if from_user_id == to_user_id:
            raise ValueError(
                "Cannot transfer to the same user"
            )

        request_data = {
            "to_user_id": str(to_user_id),
            "asset_id": str(asset_id),
            "amount": str(amount),
            "description": description,
        }

        request_hash = (
            IdempotencyService.hash_request(
                request_data
            )
        )

        # Check existing idempotency record
        existing = await IdempotencyService.get_record(
            db,
            user_id=from_user_id,
            idempotency_key=idempotency_key,
        )

        if existing:

            if existing.request_hash != request_hash:
                raise ValueError(
                    "Idempotency key was already used "
                    "with a different request"
                )

            if existing.transaction_id is None:
                raise ValueError(
                    "Previous transaction is still processing"
                )

            return existing.transaction_id

        # Fetch accounts.
        result = await db.execute(
            select(Account)
            .where(
                Account.user_id.in_(
                    [from_user_id, to_user_id]
                ),
                Account.asset_id == asset_id,
                Account.account_type == "CUSTOMER",
            )
            .order_by(Account.user_id)
            .with_for_update()
        )

        accounts = result.scalars().all()

        account_by_user = {
            account.user_id: account
            for account in accounts
        }

        source_account = account_by_user.get(
            from_user_id
        )

        destination_account = account_by_user.get(
            to_user_id
        )

        if source_account is None:
            raise ValueError(
                "Source account does not exist"
            )

        if destination_account is None:
            raise ValueError(
                "Destination account does not exist"
            )

        if source_account.id == destination_account.id:
            raise ValueError(
                "Source and destination accounts cannot be same"
            )

        # Check available balance.
        if source_account.available_balance < amount:
            raise ValueError(
                "Insufficient available balance"
            )

        # Create idempotency record.
        idempotency = IdempotencyRecord(
            user_id=from_user_id,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            status="PROCESSING",
        )

        db.add(idempotency)

        try:

            await db.flush()

        except IntegrityError:

            await db.rollback()

            existing = await IdempotencyService.get_record(
                db,
                user_id=from_user_id,
                idempotency_key=idempotency_key,
            )

            if existing and existing.transaction_id:
                return existing.transaction_id

            raise

        # Balance changes
        await BalanceService.debit(
            source_account,
            amount,
        )

        await BalanceService.credit(
            destination_account,
            amount,
        )

        # Ledger
        transaction = (
            await LedgerService.create_transaction(
                db,
                transaction_type="TRANSFER",
                entries=[
                    {
                        "account_id": source_account.id,
                        "entry_type": "DEBIT",
                        "amount": amount,
                    },
                    {
                        "account_id": destination_account.id,
                        "entry_type": "CREDIT",
                        "amount": amount,
                    },
                ],
                description=description,
            )
        )

        idempotency.transaction_id = transaction.id
        idempotency.status = "COMPLETED"

        idempotency.response_data = json.dumps(
            {
                "transaction_id": str(transaction.id),
                "reference": transaction.reference,
                "status": transaction.status,
            }
        )

        await db.commit()

        return transaction