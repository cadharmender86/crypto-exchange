from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.asset import Asset
from app.models.user import User
from app.services.balance_service import BalanceService
from app.services.ledger_service import LedgerService


class TestDepositService:
    """Development-only minting service.

    A test deposit is represented as a transfer from a dedicated system
    treasury account to the customer's account. This keeps the ledger
    balanced and makes the test funds visible in reconciliation.
    """

    SYSTEM_EMAIL = "system-test-treasury@bitnova.local"
    SYSTEM_ACCOUNT_TYPE = "SYSTEM_TREASURY"
    CUSTOMER_ACCOUNT_TYPE = "CUSTOMER"

    @staticmethod
    async def _get_or_create_system_user(db: AsyncSession) -> User:
        result = await db.execute(
            select(User)
            .where(User.email == TestDepositService.SYSTEM_EMAIL)
            .with_for_update()
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                email=TestDepositService.SYSTEM_EMAIL,
                password_hash="!SYSTEM_ACCOUNT_NO_LOGIN!",
                is_active=True,
                is_verified=True,
                two_factor_enabled=False,
            )
            db.add(user)
            await db.flush()

        return user

    @staticmethod
    async def _get_or_create_account(
        db: AsyncSession,
        *,
        user_id: UUID,
        asset_id: UUID,
        account_type: str,
    ) -> Account:
        result = await db.execute(
            select(Account)
            .where(
                Account.user_id == user_id,
                Account.asset_id == asset_id,
                Account.account_type == account_type,
            )
            .with_for_update()
        )
        account = result.scalar_one_or_none()

        if account is None:
            account = Account(
                user_id=user_id,
                asset_id=asset_id,
                account_type=account_type,
                available_balance=Decimal("0"),
                locked_balance=Decimal("0"),
                status="ACTIVE",
            )
            db.add(account)
            await db.flush()

        BalanceService._validate_account(account)
        return account

    @staticmethod
    async def deposit(
        db: AsyncSession,
        *,
        user_id: UUID,
        asset_id: UUID,
        amount: Decimal,
        description: str | None = None,
    ):
        amount = BalanceService._amount(amount)

        asset_result = await db.execute(
            select(Asset)
            .where(Asset.id == asset_id)
            .with_for_update()
        )
        asset = asset_result.scalar_one_or_none()

        if asset is None:
            raise ValueError("Asset not found")
        if not asset.is_active:
            raise ValueError("Asset is inactive")
        if not asset.deposit_enabled:
            raise ValueError("Deposits are disabled for this asset")

        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if user is None:
            raise ValueError("User not found")
        if not user.is_active:
            raise ValueError("User account is inactive")

        treasury_user = await TestDepositService._get_or_create_system_user(db)

        treasury = await TestDepositService._get_or_create_account(
            db,
            user_id=treasury_user.id,
            asset_id=asset_id,
            account_type=TestDepositService.SYSTEM_ACCOUNT_TYPE,
        )

        customer = await TestDepositService._get_or_create_account(
            db,
            user_id=user_id,
            asset_id=asset_id,
            account_type=TestDepositService.CUSTOMER_ACCOUNT_TYPE,
        )

        await BalanceService.debit(treasury, amount)
        await BalanceService.credit(customer, amount)

        transaction = await LedgerService.create_transaction(
            db,
            transaction_type="TEST_DEPOSIT",
            entries=[
                {
                    "account_id": treasury.id,
                    "entry_type": "DEBIT",
                    "amount": amount,
                },
                {
                    "account_id": customer.id,
                    "entry_type": "CREDIT",
                    "amount": amount,
                },
            ],
            description=description or f"Development test deposit of {amount} {asset.symbol}",
        )

        return transaction, customer
