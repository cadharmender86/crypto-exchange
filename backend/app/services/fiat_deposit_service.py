from decimal import Decimal
from uuid import UUID
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import AuditLog
from app.models.ledger_transaction import LedgerTransaction
from app.models.fiat_transaction import FiatTransactionType
from app.models.bank_account import (
    BankAccount,
    BankAccountStatus,
)
from app.models.fiat_deposit import (
    FiatDeposit,
    FiatDepositStatus,
)
from app.services.fiat_balance_service import FiatBalanceService


class FiatDepositService:
    """
    Manual INR deposit workflow.

    Responsibilities:
    - Accept user INR deposit requests.
    - Validate bank account ownership.
    - Validate UTR uniqueness.
    - Create PENDING fiat deposit requests.

    This service DOES NOT credit the INR wallet.
    Wallet credit happens only during admin approval.
    """

    SUPPORTED_CURRENCY = "INR"

    INR_PRECISION = Decimal("0.01")

    MIN_DEPOSIT_AMOUNT = Decimal("1.00")
    MAX_DEPOSIT_AMOUNT = Decimal("10000000.00")

    def __init__(self, db: AsyncSession):
        self.db = db
        self.balance_service = FiatBalanceService(db)

    async def submit_deposit(
        self,
        user_id: UUID,
        bank_account_id: UUID,
        amount: Decimal,
        utr_number: str,
        remarks: str | None = None,
        provider_metadata: dict | None = None,
    ) -> FiatDeposit:
        """
        Create a pending INR deposit request.

        Args:
            user_id: Deposit owner.
            bank_account_id: Verified bank account used for transfer.
            amount: Deposit amount.
            utr_number: IMPS/NEFT/RTGS/UPI transaction reference.
            remarks: Optional user remarks.
            provider_metadata: Optional payment gateway metadata.

        Returns:
            FiatDeposit object.

        Raises:
            TypeError
            ValueError
            PermissionError
        """

        # -----------------------------
        # Amount Validation
        # -----------------------------
        if not isinstance(amount, Decimal):
            raise TypeError("amount must be Decimal.")

        amount = amount.quantize(self.INR_PRECISION)

        if amount < self.MIN_DEPOSIT_AMOUNT:
            raise ValueError(
                f"Minimum deposit amount is {self.MIN_DEPOSIT_AMOUNT} INR."
            )

        if amount > self.MAX_DEPOSIT_AMOUNT:
            raise ValueError(
                f"Maximum deposit amount is {self.MAX_DEPOSIT_AMOUNT} INR."
            )

        # -----------------------------
        # UTR Validation
        # -----------------------------
        utr_number = utr_number.strip().upper()

        if not utr_number:
            raise ValueError("UTR number is required.")

        if len(utr_number) < 8 or len(utr_number) > 50:
            raise ValueError("Invalid UTR number length.")

        if not utr_number.isalnum():
            raise ValueError("UTR must contain only letters and numbers.")

        # -----------------------------
        # Bank Account Validation
        # -----------------------------
        bank_account = await self.db.scalar(
            select(BankAccount)
            .where(
                BankAccount.id == bank_account_id,
                BankAccount.user_id == user_id,
            )
            .with_for_update()
        )

        if bank_account is None:
            raise ValueError("Bank account not found.")

        if bank_account.status != BankAccountStatus.VERIFIED:
            raise PermissionError("Bank account is not verified.")

        # -----------------------------
        # Duplicate UTR Check
        # -----------------------------
        existing = await self.db.scalar(
            select(FiatDeposit)
            .where(FiatDeposit.utr_number == utr_number)
            .with_for_update()
        )

        if existing:
            raise ValueError("UTR already submitted.")

        # -----------------------------
        # Create Pending Deposit
        # -----------------------------
        deposit = FiatDeposit(
            user_id=user_id,
            bank_account_id=bank_account.id,
            currency=self.SUPPORTED_CURRENCY,
            amount=amount,
            utr_number=utr_number,
            status=FiatDepositStatus.PENDING,
            remarks=remarks.strip() if remarks else None,
            provider_metadata=provider_metadata or {},
        )

        self.db.add(deposit)

        # Persist without committing.
        await self.db.flush()

        return deposit

    async def approve_deposit(
        self,
        deposit_id: UUID,
        approved_by_admin_id: UUID,
        remarks: str | None = None,
    ) -> FiatDeposit:
        """
        Approve a pending INR deposit and credit the user's fiat wallet.

        This operation is atomic. If any step fails, the transaction
        is rolled back by the caller.
        """

        # -----------------------------
        # Lock Deposit
        # -----------------------------
        deposit = await self.db.scalar(
            select(FiatDeposit)
            .where(FiatDeposit.id == deposit_id)
            .with_for_update()
        )

        if deposit is None:
            raise ValueError("Fiat deposit not found.")

        if deposit.status == FiatDepositStatus.APPROVED:
            raise ValueError("Deposit already approved.")

        if deposit.status == FiatDepositStatus.REJECTED:
            raise ValueError("Rejected deposits cannot be approved.")

        if deposit.status == FiatDepositStatus.EXPIRED:
            raise ValueError("Expired deposits cannot be approved.")

        if deposit.status != FiatDepositStatus.PENDING:
            raise ValueError("Deposit is not pending.")

        # -----------------------------
        # Create Ledger Transaction
        # -----------------------------
        ledger_tx = LedgerTransaction(
            reference=f"FIATDEP-{deposit.utr_number}",
            transaction_type="FIAT_DEPOSIT",
            status="POSTED",
            description=f"INR Deposit {deposit.utr_number}",
        )

        self.db.add(ledger_tx)
        await self.db.flush()

        # -----------------------------
        # Credit INR Wallet
        # -----------------------------
        fiat_tx = await self.balance_service.credit(
            user_id=deposit.user_id,
            amount=deposit.amount,
            transaction_type=FiatTransactionType.INR_DEPOSIT,
            reference_type="fiat_deposit",
            reference_id=str(deposit.id),
            description=f"Approved INR Deposit ({deposit.utr_number})",
            idempotency_key=f"fiat-deposit-{deposit.id}",
        )

        # -----------------------------
        # Update Deposit Status
        # -----------------------------
        deposit.status = FiatDepositStatus.APPROVED
        deposit.ledger_transaction_id = ledger_tx.id
        deposit.approved_by_admin_id = approved_by_admin_id
        deposit.approved_at = datetime.now(timezone.utc)
        deposit.remarks = remarks.strip() if remarks else deposit.remarks

        self.db.add(
            AuditLog(
                admin_user_id=approved_by_admin_id,
                action="FIAT_DEPOSIT_APPROVED",
                resource_type="FIAT_DEPOSIT",
                resource_id=str(deposit.id),
                reson=remarks,
                result="SUCCESS",
            )
        )
        await self.db.flush()

        return deposit
    async def reject_deposit(
        self,
        deposit_id: UUID,
        rejected_by_admin_id: UUID,
        rejection_reason: str,
    ) -> FiatDeposit:
        """
        Reject a pending INR deposit.
        """

        deposit = await self.db.scalar(
            select(FiatDeposit)
            .where(FiatDeposit.id == deposit_id)
            .with_for_update()
        )

        if deposit is None:
            raise ValueError("Fiat deposit not found.")

        if deposit.status != FiatDepositStatus.PENDING:
            raise ValueError("Only pending deposits can be rejected.")

        rejection_reason = rejection_reason.strip()

        if not rejection_reason:
            raise ValueError("Rejection reason is required.")

        deposit.status = FiatDepositStatus.REJECTED
        deposit.rejection_reason = rejection_reason
        deposit.approved_by_admin_id = rejected_by_admin_id
        deposit.approved_at = datetime.now(timezone.utc)

        self.db.add(
            AuditLog(
                admin_user_id=rejected_by_admin_id,
                action="FIAT_DEPOSIT_REJECTED",
                resource_type="FIAT_DEPOSIT",
                resource_id=str(deposit.id),
                reason=rejection_reason,
                result="SUCCESS",
            )
        )
        await self.db.flush()

        return deposit

    async def expire_pending_deposits(
        self,
        expiry_hours: int = 24,
    ) -> int:
        """
        Expire pending deposits older than expiry_hours.

        Returns:
            Number of expired deposits.
        """

        cutoff = datetime.now(timezone.utc) - timedelta(hours=expiry_hours)

        result = await self.db.execute(
            select(FiatDeposit)
            .where(
                FiatDeposit.status == FiatDepositStatus.PENDING,
                FiatDeposit.created_at < cutoff,
            )
            .with_for_update()
        )

        deposits = result.scalars().all()

        for deposit in deposits:
            deposit.status = FiatDepositStatus.EXPIRED

        self.db.add(
            AuditLog(
                action="FIAT_DEPOSIT_EXPIRED",
                resource_type="FIAT_DEPOSIT",
                resource_id=str(deposit.id),
                reason=f"Automatically expired after {expiry_hours} hours.",
                result="SUCCESS",
            )
        )
        await self.db.flush()

        return len(deposits)

    async def get_user_deposits(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FiatDeposit]:
        """
        Return user's fiat deposit history.
        """

        result = await self.db.execute(
            select(FiatDeposit)
            .where(FiatDeposit.user_id == user_id)
            .order_by(FiatDeposit.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().all())

    async def get_pending_deposits(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[FiatDeposit]:
        """
        Return pending fiat deposits for admin review.
        """

        result = await self.db.execute(
            select(FiatDeposit)
            .options(
                selectinload(FiatDeposit.user),
                selectinload(FiatDeposit.bank_account),
            )
            .where(FiatDeposit.status == FiatDepositStatus.PENDING)
            .order_by(FiatDeposit.created_at.asc())
            .limit(limit)
            .offset(offset)
        )

        return list(result.scalars().all())