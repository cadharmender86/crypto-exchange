from decimal import Decimal
from uuid import UUID, uuid4
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.account import Account
from app.models.ledger_entry import LedgerEntry, LedgerEntryType
from app.models.ledger_transaction import (
    LedgerTransaction,
    LedgerTransactionType,
    LedgerTransactionStatus,
)
from app.services.balance_service import BalanceService


class LedgerService:

    @staticmethod
    async def create_transaction(
        db: AsyncSession,
        *,
        user_id: UUID,
        reference: str | None = None,
        transaction_type: LedgerTransactionType,
        entries: list[dict],
        description: str | None = None,
    ) -> LedgerTransaction:

        if len(entries) < 2:
            raise ValueError(
                "A ledger transaction requires at least two entries"
            )

        debit_total = Decimal("0")
        credit_total = Decimal("0")

        for entry in entries:

            amount = Decimal(str(entry["amount"]))

            if amount <= 0:
                raise ValueError(
                    "Ledger amount must be greater than zero"
                )

            entry_type = entry["entry_type"]

            if entry_type == "DEBIT":
                debit_total += amount

            elif entry_type == "CREDIT":
                credit_total += amount

            else:
                raise ValueError(
                    f"Invalid entry type: {entry_type}"
                )

        if debit_total != credit_total:
            raise ValueError(
                f"Unbalanced ledger transaction: "
                f"debit={debit_total}, "
                f"credit={credit_total}"
            )

        existing = await db.execute(
            select(LedgerTransaction).where(
                LedgerTransaction.reference == reference
            )
        )

        existing_transaction = existing.scalar_one_or_none()

        if existing_transaction:
            return existing_transaction

        transaction = LedgerTransaction(
            user_id=user_id,
            reference=reference or f"{transaction_type.value}-{uuid4().hex[:16].upper()}",
            transaction_type=transaction_type,
            status=LedgerTransactionStatus.POSTED,
            description=description,
        )

        db.add(transaction)

        await db.flush()

        for entry in entries:

            account = await BalanceService.get_locked_account(
                db,
                entry["account_id"],
            )

            amount = Decimal(str(entry["amount"]))

            if entry["entry_type"] == LedgerEntryType.CREDIT:
                await BalanceService.credit(account,amount)

            elif entry["entry_type"] == LedgerEntryType.DEBIT:
                await BalanceService.debit(account, amount)    

            ledger_entry = LedgerEntry(
                transaction_id=transaction.id,
                account_id=entry["account_id"],
                entry_type=entry["entry_type"],
                amount=Decimal(str(entry["amount"])),
            )

            db.add(ledger_entry)

        await db.flush()

        return transaction

    @staticmethod
    async def get_user_transactions(
        db: AsyncSession,
        *,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[LedgerTransaction]:

        result = await db.execute(
            select(LedgerTransaction)
            .where(LedgerTransaction.user_id == user_id)
            .order_by(LedgerTransaction.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().unique().all()

    @staticmethod
    async def list_user_transactions(
        db: AsyncSession,
        user_id: UUID,
    ) -> list[LedgerTransaction]:

        result = await db.execute(
            select(LedgerTransaction)
            .where(LedgerTransaction.user_id == user_id)
            .options(selectinload(LedgerTransaction.ledger_entries))
            .order_by(LedgerTransaction.created_at.desc())
        )

        return result.scalars().unique().all()