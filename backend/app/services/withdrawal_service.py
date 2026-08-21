from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.asset import Asset
from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.services.balance_service import BalanceService
from app.services.ledger_service import LedgerService

class WithdrawalService:
    """
    Withdrawal lifecycle service.

    This service only mutates database state.
    The caller is responsible for commit/rollback.
    """

    SYSTEM_ACCOUNT_TYPE = "SYSTEM_TREASURY"
    CUSTOMER_ACCOUNT_TYPE = "CUSTOMER"
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

        # --------------------------------------------------------
        # Validate asset
        # --------------------------------------------------------

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

        if not asset.withdrawal_enabled:
            raise ValueError(
                "Withdrawals are disabled for this asset"
            )

        # --------------------------------------------------------
        # Idempotency
        # --------------------------------------------------------

        existing_result = await db.execute(
            select(Withdrawal)
            .where(
                Withdrawal.user_id == user_id,
                Withdrawal.idempotency_key == idempotency_key,
            )
        )

        existing = existing_result.scalar_one_or_none()

        if existing is not None:
            if (
                existing.asset_id != asset_id
                or existing.network != network
                or existing.destination_address != destination_address
                or existing.amount != amount
            ):
                raise ValueError(
                    "Idempotency key already used with different withdrawal parameters"
                )

            return existing

        # --------------------------------------------------------
        # Lock customer account
        # --------------------------------------------------------

        customer_result = await db.execute(
            select(Account)
            .where(
                Account.user_id == user_id,
                Account.asset_id == asset_id,
                Account.account_type
                == WithdrawalService.CUSTOMER_ACCOUNT_TYPE,
            )
            .with_for_update()
        )

        customer = customer_result.scalar_one_or_none()

        if customer is None:
            raise ValueError(
                "Customer account does not exist"
            )

        # --------------------------------------------------------
        # Lock withdrawal funds
        # --------------------------------------------------------

        await BalanceService.lock(customer, amount)

        # --------------------------------------------------------
        # Lock system treasury account
        # --------------------------------------------------------

        treasury_result = await db.execute(
            select(Account)
            .where(
                Account.account_type
                == WithdrawalService.SYSTEM_ACCOUNT_TYPE,
                Account.asset_id == asset_id,
            )
            .with_for_update()
        )

        treasury = treasury_result.scalar_one_or_none()

        if treasury is None:
            raise ValueError(
                "System treasury account does not exist"
            )

        BalanceService._validate_account(treasury)

        # Treasury must have enough available balance before a withdrawal
        if treasury.available_balance < amount:
            raise ValueError(
                "System treasury has insufficient balance for withdrawal"
            )

        # --------------------------------------------------------
        # Create withdrawal
        # --------------------------------------------------------

        withdrawal = Withdrawal(
            user_id=user_id,
            account_id=customer.id,
            asset_id=asset_id,
            network=network,
            destination_address=destination_address,
            amount=amount,
            status=WithdrawalStatus.PENDING.value,
            idempotency_key=idempotency_key,
        )

        db.add(withdrawal)

        await db.flush()

        # --------------------------------------------------------
        # Balanced ledger transaction
        # --------------------------------------------------------

        transaction = await LedgerService.create_transaction(
            db,
            transaction_type="WITHDRAWAL",
            entries=[
                {
                    "account_id": customer.id,
                    "entry_type": "DEBIT",
                    "amount": amount,
                },
                {
                    "account_id": treasury.id,
                    "entry_type": "CREDIT",
                    "amount": amount,
                },
            ],
            description=(
                f"Customer withdrawal "
                f"{network}:{destination_address}"
            ),
        )

        withdrawal.ledger_transaction_id = transaction.id

        await db.flush()

        return withdrawal


    @staticmethod
    async def approve_withdrawal(
        db: AsyncSession,
        withdrawal: Withdrawal,
    ) -> Withdrawal:

        if withdrawal.status != WithdrawalStatus.PENDING.value:
            raise ValueError("Only pending withdrawals can be approved")

        withdrawal.status = WithdrawalStatus.APPROVED.value

        await db.flush()

        return withdrawal


    @staticmethod
    async def mark_broadcasting(
        db: AsyncSession,
        withdrawal: Withdrawal,
    ) -> Withdrawal:

        if withdrawal.status != WithdrawalStatus.APPROVED.value:
            raise ValueError("Withdrawal must be approved before broadcasting")

        withdrawal.status = WithdrawalStatus.BROADCASTING.value

        await db.flush()

        return withdrawal


    @staticmethod
    async def mark_broadcasted(
        db: AsyncSession,
        withdrawal: Withdrawal,
        tx_hash: str,
    ) -> Withdrawal:

        withdrawal.status = WithdrawalStatus.BROADCASTED.value
        withdrawal.blockchain_tx_hash = tx_hash.lower()
        withdrawal.failure_reason = None
        withdrawal.confirmations = 0
        withdrawal.broadcasted_at = datetime.now(timezone.utc)

        await db.flush()

        return withdrawal

    @staticmethod
    async def mark_failed(
        db: AsyncSession,
        withdrawal: Withdrawal,
        reason: str,
    ) -> Withdrawal:
        """
        Mark a withdrawal as failed during blockchain broadcast.
        """

        withdrawal.status = WithdrawalStatus.FAILED.value
        withdrawal.failure_reason = reason[:255]

        await db.flush()

        return withdrawal

    @staticmethod
    async def approve_by_admin(
        db: AsyncSession,
        withdrawal: Withdrawal,
    ) -> Withdrawal:
        """
        Approve a pending withdrawal.
        """

        if withdrawal.status != WithdrawalStatus.PENDING.value:
            raise ValueError(
                f"Withdrawal is already {withdrawal.status.lower()}"
            )

        withdrawal.status = WithdrawalStatus.APPROVED.value

        await db.flush()

        return withdrawal

    @staticmethod
    async def reject_by_admin(
        db: AsyncSession,
        withdrawal: Withdrawal,
    ) -> Withdrawal:
        """
        Reject a pending withdrawal and unlock customer funds.
        """

        if withdrawal.status != WithdrawalStatus.PENDING.value:
            raise ValueError(
                f"Withdrawal is already {withdrawal.status.lower()}"
            )

        account = await BalanceService.get_locked_account(
            db,
            withdrawal.account_id,
        )

        await BalanceService.unlock(account, withdrawal.amount)

        withdrawal.status = WithdrawalStatus.REJECTED.value

        await db.flush()

        return withdrawal