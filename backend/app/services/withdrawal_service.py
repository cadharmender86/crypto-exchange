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
    """Provider-independent withdrawal creation and internal settlement.

    The service deliberately does not commit. The caller owns the database
    transaction so the withdrawal, balance lock, and ledger entries are
    committed or rolled back atomically.
    """

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

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
            status=WithdrawalService.PENDING,
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
    async def set_blockchain_tx_hash(
        db: AsyncSession,
        *,
        withdrawal_id: UUID,
        blockchain_tx_hash: str,
    ) -> Withdrawal:
        """Attach the blockchain transaction hash to a withdrawal."""

        blockchain_tx_hash = blockchain_tx_hash.strip()

        if not blockchain_tx_hash:
            raise ValueError(
                "Blockchain transaction hash is required"
            )

        result = await db.execute(
            select(Withdrawal)
            .where(Withdrawal.id == withdrawal_id)
            .with_for_update()
        )

        withdrawal = result.scalar_one_or_none()

        if withdrawal is None:
            raise ValueError("Withdrawal not found")

        if withdrawal.status == WithdrawalService.FAILED:
            raise ValueError(
                "Cannot track a failed withdrawal"
            )

        if withdrawal.blockchain_tx_hash is not None:
            if withdrawal.blockchain_tx_hash != blockchain_tx_hash:
                raise ValueError(
                    "Withdrawal already has a different "
                    "blockchain transaction hash"
                )

            return withdrawal

        withdrawal.blockchain_tx_hash = blockchain_tx_hash

        await db.flush()

        return withdrawal