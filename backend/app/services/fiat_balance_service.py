from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fiat_account import FiatAccount, FiatAccountStatus
from app.models.fiat_transaction import (
    FiatTransaction,
    FiatTransactionStatus,
    FiatTransactionType,
)


class FiatBalanceService:
    """
    Atomic INR balance operations.

    Every INR balance change in BitNova must use this service.
    """
    SUPPORTED_FIAT = {"INR"}
    INR_PRECISION = Decimal("0.01")
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_account(
        self,
        user_id: UUID,
        currency: str = "INR",
    ) -> FiatAccount:
        """
        Return user's INR account.
        Create it automatically if it doesn't exist.
        """

        currency = currency.upper()

        if currency not in self.SUPPORTED_FIAT:
            raise ValueError(f"Unsupported fiat currency: {currency}")
                        
        result = await self.db.execute(
            select(FiatAccount)
            .where(
                FiatAccount.user_id == user_id,
                FiatAccount.currency == currency,
            )
            .with_for_update()
        )

        account = result.scalar_one_or_none()

        if account:
            return account

        account = FiatAccount(
            user_id=user_id,
            currency=currency,
            available_balance=Decimal("0"),
            locked_balance=Decimal("0"),
            status=FiatAccountStatus.ACTIVE,
        )

        self.db.add(account)
        await self.db.flush()

        return account

    async def credit(
        self,
        user_id: UUID,
        amount: Decimal,
        transaction_type: FiatTransactionType,
        reference_type: str,
        reference_id: str,
        description: str | None = None,
        idempotency_key: str | None = None,
    ) -> FiatTransaction:
        """
        Credit INR into user's fiat wallet.

        Example:
            Deposit approved.
            Refund.
            Trade sell proceeds.
        """
        if not isinstance(transaction_type, FiatTransactionType):
            raise TypeError("transaction_type must be FiatTransactionType.")

        if idempotency_key:
            existing = await self.db.scalar(
                select(FiatTransaction).where(
                    FiatTransaction.user_id == user_id,
                    FiatTransaction.idempotency_key == idempotency_key,
                )
            )

            if existing:
                return existing

        if not isinstance(amount, Decimal):
            raise TypeError("amount must be Decimal.")    
    
        if amount <= Decimal("0"):
            raise ValueError("Amount must be greater than zero.")

        amount = amount.quantize(self.INR_PRECISION)

        reference_type = reference_type.strip()
        reference_id = reference_id.strip()

        if not reference_type.strip():
            raise ValueError("reference_type is required.")

        if not reference_id.strip():
            raise ValueError("reference_id is required.")

        account = await self.get_or_create_account(user_id)

        if account.status == FiatAccountStatus.FROZEN:
            raise PermissionError("Fiat account is frozen.")

        if account.status == FiatAccountStatus.CLOSED:
            raise PermissionError("Fiat account is closed.")

        new_balance = account.available_balance + amount

        account.available_balance = new_balance

        transaction = FiatTransaction(
            fiat_account_id=account.id,
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=new_balance,
            reference_type=reference_type,
            reference_id=reference_id,
            status=FiatTransactionStatus.COMPLETED,
            description=description,
            idempotency_key=idempotency_key,
        )

        self.db.add(transaction)

        # Flush inserts/updates without committing.
        await self.db.flush()
        await self.db.refresh(transaction)

        return transaction