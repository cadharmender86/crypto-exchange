from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.asset import Asset
from app.models.bank_account import BankAccountStatus
from app.models.fiat_deposit import FiatDeposit, FiatDepositStatus
from app.models.fiat_transaction import FiatTransactionType
from app.models.ledger_entry import LedgerEntry
from app.models.ledger_transaction import LedgerTransaction
from app.services.fiat_balance_service import FiatBalanceService


class AdminFiatDepositService:
    """
    Admin workflow for manual INR deposits.

    - Approves pending INR deposits.
    - Creates immutable ledger transaction.
    - Creates double-entry ledger entries.
    - Credits customer's INR fiat wallet.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.balance_service = FiatBalanceService(db)

    async def _get_inr_asset(self) -> Asset:
        asset = await self.db.scalar(
            select(Asset).where(Asset.symbol == "INR")
        )
        if asset is None:
            raise ValueError("INR asset not found.")
        return asset

    async def _get_user_inr_account(
        self,
        user_id: UUID,
        currency: str,
    ) -> Account:
        """
        Returns the customer's SPOT account for the given currency (INR).
        """

        result = await self.db.execute(
            select(Account)
            .join(Asset, Account.asset_id == Asset.id)
            .where(
                Account.user_id == user_id,
                Account.account_type == "CUSTOMER",
                Account.status == "ACTIVE",
                Asset.symbol == currency,
            )
        )

        account = result.scalar_one_or_none()

        if account is None:
            raise ValueError(f"User {currency} account not found.")

        return account

    async def _get_platform_inr_account(self) -> Account:
        result = await self.db.execute(
            select(Account)
            .join(Asset, Account.asset_id == Asset.id)
            .where(
                Account.account_type == "TREASURY",
                Asset.symbol == "INR",
                Account.status == "ACTIVE",
            )
        )

        account = result.scalar_one_or_none()

        if account is None:
            raise ValueError("Platform INR settlement account not found.")

        return account

    async def approve(
        self,
        deposit_id: UUID,
        admin_user_id: UUID,
    ) -> FiatDeposit:

        result = await self.db.execute(
            select(FiatDeposit)
            .where(FiatDeposit.id == deposit_id)
            .with_for_update()
        )

        deposit = result.scalar_one_or_none()

        if deposit is None:
            raise ValueError("Deposit not found.")

        if deposit.status != FiatDepositStatus.PENDING:
            raise ValueError("Only pending deposits can be approved.")

        if deposit.ledger_transaction_id is not None:
            raise ValueError("Deposit already approved.")

        bank_account = deposit.bank_account

        if bank_account is None:
            raise ValueError("Bank account not found.")

        if bank_account.status != BankAccountStatus.VERIFIED:
            raise ValueError("Bank account is not verified.")

        # ---------------------------------------------------------
        # Resolve INR asset and ledger accounts
        # ---------------------------------------------------------

        inr_asset = await self._get_inr_asset()

        user_inr_account = await self._get_user_inr_account(
            deposit.user_id,
            deposit.currency,
        )

        platform_inr_account = await self._get_platform_inr_account()

        # ---------------------------------------------------------
        # Immutable ledger transaction
        # ---------------------------------------------------------

        ledger_transaction = LedgerTransaction(
            reference=f"INR-DEP-{deposit.id}",
            transaction_type="FIAT_DEPOSIT",
            status="POSTED",
            description=f"Manual INR deposit ({deposit.utr_number})",
        )

        self.db.add(ledger_transaction)
        await self.db.flush()

        # ---------------------------------------------------------
        # Double-entry bookkeeping
        # ---------------------------------------------------------

        self.db.add_all(
            [
                LedgerEntry(
                    transaction_id=ledger_transaction.id,
                    account_id=platform_inr_account.id,
                    entry_type="DEBIT",
                    amount=Decimal(deposit.amount),
                ),
                LedgerEntry(
                    transaction_id=ledger_transaction.id,
                    account_id=user_inr_account.id,
                    entry_type="CREDIT",
                    amount=Decimal(deposit.amount),
                ),
            ]
        )

        await self.db.flush()

        # ---------------------------------------------------------
        # Credit Fiat Wallet
        # ---------------------------------------------------------

        await self.balance_service.credit(
            user_id=deposit.user_id,
            amount=Decimal(deposit.amount),
            transaction_type=FiatTransactionType.INR_DEPOSIT,
            reference_type="FIAT_DEPOSIT",
            reference_id=str(deposit.id),
            description=f"Approved INR Deposit (UTR {deposit.utr_number})",
            idempotency_key=f"fiat-deposit-{deposit.id}",
        )

        # ---------------------------------------------------------
        # Update Deposit
        # ---------------------------------------------------------

        deposit.status = FiatDepositStatus.APPROVED
        deposit.ledger_transaction_id = ledger_transaction.id
        deposit.approved_by_admin_id = admin_user_id
        deposit.approved_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(deposit)

        return deposit

    async def reject(
        self,
        deposit_id: UUID,
        admin_user_id: UUID,
        rejection_reason: str,
    ) -> FiatDeposit:

        result = await self.db.execute(
            select(FiatDeposit)
            .where(FiatDeposit.id == deposit_id)
            .with_for_update()
        )

        deposit = result.scalar_one_or_none()

        if deposit is None:
            raise ValueError("Deposit not found.")

        if deposit.status != FiatDepositStatus.PENDING:
            raise ValueError("Only pending deposits can be rejected.")

        rejection_reason = rejection_reason.strip()

        if not rejection_reason:
            raise ValueError("Rejection reason is required.")

        deposit.status = FiatDepositStatus.REJECTED
        deposit.rejection_reason = rejection_reason
        deposit.approved_by_admin_id = admin_user_id
        deposit.approved_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(deposit)

        return deposit