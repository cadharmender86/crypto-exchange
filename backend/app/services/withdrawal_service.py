from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.asset import Asset
from app.models.withdrawal import Withdrawal
from app.services.balance_service import BalanceService
from app.services.ledger_service import LedgerService


class WithdrawalService:
    """Provider-independent withdrawal lifecycle and settlement service."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    SYSTEM_ACCOUNT_TYPE = "SYSTEM_TREASURY"
    CUSTOMER_ACCOUNT_TYPE = "CUSTOMER"

    ALLOWED_TRANSITIONS = {
        PENDING: {APPROVED, REJECTED},
        APPROVED: {PROCESSING},
        PROCESSING: {COMPLETED, FAILED},
    }

    @staticmethod
    def is_valid_transition(current_status: str, target_status: str) -> bool:
        return target_status in WithdrawalService.ALLOWED_TRANSITIONS.get(current_status, set())

    @staticmethod
    def validate_transition_amount(amount: Decimal) -> Decimal:
        return BalanceService._amount(amount)

    @staticmethod
    def _transition(withdrawal: Withdrawal, target_status: str) -> None:
        if not WithdrawalService.is_valid_transition(withdrawal.status, target_status):
            raise ValueError(
                f"Invalid withdrawal transition: {withdrawal.status} -> {target_status}"
            )
        withdrawal.status = target_status

    @staticmethod
    async def approve_withdrawal(db: AsyncSession, *, withdrawal_id: UUID) -> Withdrawal:
        result = await db.execute(select(Withdrawal).where(Withdrawal.id == withdrawal_id).with_for_update())
        withdrawal = result.scalar_one_or_none()
        if withdrawal is None:
            raise ValueError("Withdrawal not found")
        WithdrawalService._transition(withdrawal, WithdrawalService.APPROVED)
        await db.flush()
        return withdrawal

    @staticmethod
    async def reject_withdrawal(db: AsyncSession, *, withdrawal_id: UUID) -> Withdrawal:
        result = await db.execute(select(Withdrawal).where(Withdrawal.id == withdrawal_id).with_for_update())
        withdrawal = result.scalar_one_or_none()
        if withdrawal is None:
            raise ValueError("Withdrawal not found")
        account = await BalanceService.get_locked_account(db, withdrawal.account_id)
        await BalanceService.unlock(account, withdrawal.amount)
        WithdrawalService._transition(withdrawal, WithdrawalService.REJECTED)
        await db.flush()
        return withdrawal

    @staticmethod
    async def start_processing(db: AsyncSession, *, withdrawal_id: UUID) -> Withdrawal:
        result = await db.execute(select(Withdrawal).where(Withdrawal.id == withdrawal_id).with_for_update())
        withdrawal = result.scalar_one_or_none()
        if withdrawal is None:
            raise ValueError("Withdrawal not found")
        WithdrawalService._transition(withdrawal, WithdrawalService.PROCESSING)
        await db.flush()
        return withdrawal

    @staticmethod
    async def complete_withdrawal(db: AsyncSession, *, withdrawal_id: UUID) -> Withdrawal:
        result = await db.execute(select(Withdrawal).where(Withdrawal.id == withdrawal_id).with_for_update())
        withdrawal = result.scalar_one_or_none()
        if withdrawal is None:
            raise ValueError("Withdrawal not found")
        WithdrawalService._transition(withdrawal, WithdrawalService.COMPLETED)
        await db.flush()
        return withdrawal

    @staticmethod
    async def fail_withdrawal(db: AsyncSession, *, withdrawal_id: UUID) -> Withdrawal:
        result = await db.execute(select(Withdrawal).where(Withdrawal.id == withdrawal_id).with_for_update())
        withdrawal = result.scalar_one_or_none()
        if withdrawal is None:
            raise ValueError("Withdrawal not found")
        account = await BalanceService.get_locked_account(db, withdrawal.account_id)
        await BalanceService.unlock(account, withdrawal.amount)
        WithdrawalService._transition(withdrawal, WithdrawalService.FAILED)
        await db.flush()
        return withdrawal

    @staticmethod
    async def create_pending_withdrawal(
        db: AsyncSession,
        *,
        user_id: UUID,
        asset_id: UUID,
        network: str,
        destination_address: str,
        amount: Decimal,
        idempotency_key: str,
    ) -> Withdrawal:
        amount = BalanceService._amount(amount)
        network = network.strip().upper()
        destination_address = destination_address.strip()
        idempotency_key = idempotency_key.strip()
        if not network:
            raise ValueError("Network is required")
        if not destination_address:
            raise ValueError("Destination address is required")
        if not idempotency_key:
            raise ValueError("Idempotency key is required")

        asset_result = await db.execute(select(Asset).where(Asset.id == asset_id).with_for_update())
        asset = asset_result.scalar_one_or_none()
        if asset is None:
            raise ValueError("Asset not found")
        if not asset.is_active:
            raise ValueError("Asset is inactive")
        if not asset.withdrawal_enabled:
            raise ValueError("Withdrawals are disabled for this asset")

        existing_result = await db.execute(select(Withdrawal).where(Withdrawal.user_id == user_id, Withdrawal.idempotency_key == idempotency_key))
        existing = existing_result.scalar_one_or_none()
        if existing is not None:
            if existing.asset_id != asset_id or existing.network != network or existing.destination_address != destination_address or existing.amount != amount:
                raise ValueError("Idempotency key already used with different withdrawal parameters")
            return existing

        customer_result = await db.execute(select(Account).where(Account.user_id == user_id, Account.asset_id == asset_id, Account.account_type == WithdrawalService.CUSTOMER_ACCOUNT_TYPE).with_for_update())
        customer = customer_result.scalar_one_or_none()
        if customer is None:
            raise ValueError("Customer account does not exist")
        await BalanceService.lock(customer, amount)

        treasury_result = await db.execute(select(Account).where(Account.account_type == WithdrawalService.SYSTEM_ACCOUNT_TYPE, Account.asset_id == asset_id).with_for_update())
        treasury = treasury_result.scalar_one_or_none()
        if treasury is None:
            raise ValueError("System treasury account does not exist")
        BalanceService._validate_account(treasury)

        withdrawal = Withdrawal(user_id=user_id, account_id=customer.id, asset_id=asset_id, network=network, destination_address=destination_address, amount=amount, status=WithdrawalService.PENDING, idempotency_key=idempotency_key)
        db.add(withdrawal)
        await db.flush()

        transaction = await LedgerService.create_transaction(
            db,
            transaction_type="WITHDRAWAL",
            entries=[
                {"account_id": customer.id, "entry_type": "DEBIT", "amount": amount},
                {"account_id": treasury.id, "entry_type": "CREDIT", "amount": amount},
            ],
            description=f"Customer withdrawal {network}:{destination_address}",
        )
        withdrawal.ledger_transaction_id = transaction.id
        await db.flush()
        return withdrawal
