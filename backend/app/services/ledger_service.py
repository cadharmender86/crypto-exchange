from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ledger_entry import LedgerEntry
from app.models.ledger_transaction import LedgerTransaction


class LedgerService:

    @staticmethod
    async def create_transaction(
        db: AsyncSession,
        *,
        transaction_type: str,
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

        transaction = LedgerTransaction(
            reference=f"{transaction_type}-{uuid4().hex[:16].upper()}",
            transaction_type=transaction_type,
            status="POSTED",
            description=description,
        )

        db.add(transaction)

        await db.flush()

        for entry in entries:

            ledger_entry = LedgerEntry(
                transaction_id=transaction.id,
                account_id=entry["account_id"],
                entry_type=entry["entry_type"],
                amount=Decimal(str(entry["amount"])),
            )

            db.add(ledger_entry)

        await db.flush()

        return transaction