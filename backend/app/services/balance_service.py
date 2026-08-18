from decimal import Decimal, InvalidOperation
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class BalanceService:
    """Atomic balance operations for exchange accounts.

    This service deliberately does not commit transactions. The caller owns
    the database transaction so balance changes and ledger changes can be
    committed or rolled back together.
    """

    ZERO = Decimal("0")

    @staticmethod
    def _amount(amount: Decimal) -> Decimal:
        try:
            value = Decimal(str(amount))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValueError("Invalid amount") from exc

        if not value.is_finite() or value <= BalanceService.ZERO:
            raise ValueError("Amount must be a finite value greater than zero")

        return value

    @staticmethod
    def _validate_account(account: Account) -> None:
        if account.status != "ACTIVE":
            raise ValueError("Account is not active")

        available = Decimal(str(account.available_balance or 0))
        locked = Decimal(str(account.locked_balance or 0))

        if not available.is_finite() or not locked.is_finite():
            raise ValueError("Account contains an invalid balance")

        if available < BalanceService.ZERO:
            raise ValueError("Account available balance cannot be negative")

        if locked < BalanceService.ZERO:
            raise ValueError("Account locked balance cannot be negative")

    @staticmethod
    async def get_locked_account(
        db: AsyncSession,
        account_id: UUID,
    ) -> Account:
        """Load an account and acquire a PostgreSQL row lock."""
        result = await db.execute(
            select(Account)
            .where(Account.id == account_id)
            .with_for_update()
        )

        account = result.scalar_one_or_none()
        if account is None:
            raise ValueError("Account not found")

        BalanceService._validate_account(account)
        return account

    @staticmethod
    async def debit(account: Account, amount: Decimal) -> None:
        """Move funds out of available balance."""
        amount = BalanceService._amount(amount)
        BalanceService._validate_account(account)

        available = Decimal(str(account.available_balance))
        if available < amount:
            raise ValueError("Insufficient available balance")

        account.available_balance = available - amount
        BalanceService._validate_account(account)

    @staticmethod
    async def credit(account: Account, amount: Decimal) -> None:
        """Add funds to available balance."""
        amount = BalanceService._amount(amount)
        BalanceService._validate_account(account)

        available = Decimal(str(account.available_balance))
        account.available_balance = available + amount
        BalanceService._validate_account(account)

    @staticmethod
    async def lock(account: Account, amount: Decimal) -> None:
        """Move funds from available balance into locked balance."""
        amount = BalanceService._amount(amount)
        BalanceService._validate_account(account)

        available = Decimal(str(account.available_balance))
        locked = Decimal(str(account.locked_balance))

        if available < amount:
            raise ValueError("Insufficient available balance")

        account.available_balance = available - amount
        account.locked_balance = locked + amount
        BalanceService._validate_account(account)

    @staticmethod
    async def unlock(account: Account, amount: Decimal) -> None:
        """Move funds from locked balance back into available balance."""
        amount = BalanceService._amount(amount)
        BalanceService._validate_account(account)

        available = Decimal(str(account.available_balance))
        locked = Decimal(str(account.locked_balance))

        if locked < amount:
            raise ValueError("Insufficient locked balance")

        account.locked_balance = locked - amount
        account.available_balance = available + amount
        BalanceService._validate_account(account)

    @staticmethod
    async def consume_locked(
        account: Account,
        amount: Decimal,
    ) -> None:
        """Remove funds that were previously reserved in locked balance."""
        amount = BalanceService._amount(amount)
        BalanceService._validate_account(account)

        locked = Decimal(str(account.locked_balance))

        if locked < amount:
            raise ValueError("Insufficient locked balance")

        account.locked_balance = locked - amount

        BalanceService._validate_account(account)