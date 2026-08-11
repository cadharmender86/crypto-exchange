import json
from decimal import Decimal, InvalidOperation
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.idempotency import IdempotencyRecord
from app.models.ledger_transaction import LedgerTransaction
from app.services.balance_service import BalanceService
from app.services.idempotency_service import IdempotencyService
from app.services.ledger_service import LedgerService


class TransferService:
    """Atomic customer-to-customer asset transfer service.

    The database transaction is owned by this service: either balance changes,
    ledger entries, and the idempotency record are all committed, or none are.
    """

    CUSTOMER_ACCOUNT_TYPE = "CUSTOMER"

    @staticmethod
    def _validate_amount(amount: Decimal) -> Decimal:
        try:
            value = Decimal(str(amount))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValueError("Invalid transfer amount") from exc

        if not value.is_finite() or value <= 0:
            raise ValueError("Transfer amount must be a finite value greater than zero")

        return value

    @staticmethod
    async def _get_transfer_accounts(
        db: AsyncSession,
        *,
        from_user_id: UUID,
        to_user_id: UUID,
        asset_id: UUID,
    ) -> tuple[Account, Account]:
        """Lock both accounts in a deterministic order to reduce deadlocks."""
        result = await db.execute(
            select(Account)
            .where(
                Account.user_id.in_([from_user_id, to_user_id]),
                Account.asset_id == asset_id,
                Account.account_type == TransferService.CUSTOMER_ACCOUNT_TYPE,
            )
            .order_by(Account.id)
            .with_for_update()
        )

        accounts = result.scalars().all()
        account_by_user = {account.user_id: account for account in accounts}

        source = account_by_user.get(from_user_id)
        destination = account_by_user.get(to_user_id)

        if source is None:
            raise ValueError("Source account does not exist")
        if destination is None:
            raise ValueError("Destination account does not exist")
        if source.id == destination.id:
            raise ValueError("Source and destination accounts cannot be same")

        # Validate after the row lock so the validation and mutation operate
        # on the same locked database state.
        BalanceService._validate_account(source)
        BalanceService._validate_account(destination)

        return source, destination

    @staticmethod
    async def _get_completed_transaction(
        db: AsyncSession,
        record: IdempotencyRecord,
    ) -> LedgerTransaction | None:
        if record.transaction_id is None:
            return None

        result = await db.execute(
            select(LedgerTransaction).where(
                LedgerTransaction.id == record.transaction_id
            )
        )
        return result.scalar_one_or_none()

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
    ) -> LedgerTransaction:
        """Execute one idempotent, atomic transfer."""
        if not idempotency_key or not idempotency_key.strip():
            raise ValueError("Idempotency key is required")

        idempotency_key = idempotency_key.strip()
        if len(idempotency_key) > 100:
            raise ValueError("Idempotency key must not exceed 100 characters")

        amount = TransferService._validate_amount(amount)

        if from_user_id == to_user_id:
            raise ValueError("Cannot transfer to the same user")

        request_data = {
            "to_user_id": str(to_user_id),
            "asset_id": str(asset_id),
            "amount": str(amount),
            "description": description,
        }
        request_hash = IdempotencyService.hash_request(request_data)

        try:
            # Fast path for already completed requests.
            existing = await IdempotencyService.get_record(
                db,
                user_id=from_user_id,
                idempotency_key=idempotency_key,
            )

            if existing:
                if existing.request_hash != request_hash:
                    raise ValueError(
                        "Idempotency key was already used with a different request"
                    )

                transaction = await TransferService._get_completed_transaction(
                    db, existing
                )
                if transaction is not None:
                    return transaction

                raise ValueError("Previous transaction is still processing")

            # IMPORTANT: lock the source/destination accounts before creating
            # the idempotency record. Requests using the same source account
            # therefore serialize, eliminating the old race around the unique
            # (user_id, idempotency_key) constraint without rolling back an
            # unrelated caller transaction.
            source, destination = await TransferService._get_transfer_accounts(
                db,
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                asset_id=asset_id,
            )

            # Re-check idempotency after acquiring the account lock. Another
            # request may have completed while this request was waiting.
            existing = await IdempotencyService.get_record(
                db,
                user_id=from_user_id,
                idempotency_key=idempotency_key,
            )

            if existing:
                if existing.request_hash != request_hash:
                    raise ValueError(
                        "Idempotency key was already used with a different request"
                    )

                transaction = await TransferService._get_completed_transaction(
                    db, existing
                )
                if transaction is not None:
                    return transaction

                raise ValueError("Previous transaction is still processing")

            source_balance = Decimal(str(source.available_balance))
            if source_balance < amount:
                raise ValueError("Insufficient available balance")

            idempotency = IdempotencyRecord(
                user_id=from_user_id,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                status="PROCESSING",
            )
            db.add(idempotency)
            await db.flush()

            # All mutations below are part of the same DB transaction.
            await BalanceService.debit(source, amount)
            await BalanceService.credit(destination, amount)

            transaction = await LedgerService.create_transaction(
                db,
                transaction_type="TRANSFER",
                entries=[
                    {
                        "account_id": source.id,
                        "entry_type": "DEBIT",
                        "amount": amount,
                    },
                    {
                        "account_id": destination.id,
                        "entry_type": "CREDIT",
                        "amount": amount,
                    },
                ],
                description=description,
            )

            idempotency.transaction_id = transaction.id
            idempotency.status = "COMPLETED"
            idempotency.response_data = json.dumps(
                {
                    "transaction_id": str(transaction.id),
                    "reference": transaction.reference,
                    "status": transaction.status,
                },
                separators=(",", ":"),
            )

            await db.commit()

            # The transaction object is already populated by LedgerService and
            # remains suitable for the API response after commit.
            return transaction

        except Exception:
            # Never leave a partial balance/ledger/idempotency mutation behind.
            await db.rollback()
            raise
