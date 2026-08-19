from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.asset import Asset
from app.models.deposit import Deposit
from app.models.wallet import Wallet
from app.models.wallet_address import WalletAddress
from app.services.balance_service import BalanceService
from app.services.ledger_service import LedgerService


class DepositService:
    """Provider-independent deposit lifecycle and settlement service.

    This service deliberately does not commit. The caller owns the database
    transaction so deposit state, balance changes, and ledger entries are
    committed or rolled back atomically.
    """

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CREDITED = "CREDITED"
    FAILED = "FAILED"

    SYSTEM_ACCOUNT_TYPE = "SYSTEM_TREASURY"
    CUSTOMER_ACCOUNT_TYPE = "CUSTOMER"

    @staticmethod
    async def create_pending_deposit(
        db: AsyncSession,
        *,
        user_id: UUID,
        wallet_address_id: UUID,
        asset_id: UUID,
        network: str,
        blockchain_tx_hash: str,
        amount: Decimal,
        confirmations: int = 0,
        blockchain_log_index: int | None = None,
    ) -> Deposit:
        """Create or return a deposit observed on the blockchain.

        ERC-20 transactions can contain multiple Transfer logs, so a log
        index is accepted when the provider exposes one. This operation does
        not credit the customer balance.
        """

        amount = BalanceService._amount(amount)

        if confirmations < 0:
            raise ValueError("Confirmations cannot be negative")
        if blockchain_log_index is not None and blockchain_log_index < 0:
            raise ValueError("Blockchain log index cannot be negative")

        network = network.strip().upper()
        blockchain_tx_hash = blockchain_tx_hash.strip()

        if not network:
            raise ValueError("Network is required")
        if not blockchain_tx_hash:
            raise ValueError("Blockchain transaction hash is required")

        asset_result = await db.execute(
            select(Asset).where(Asset.id == asset_id).with_for_update()
        )
        asset = asset_result.scalar_one_or_none()
        if asset is None:
            raise ValueError("Asset not found")
        if not asset.is_active:
            raise ValueError("Asset is inactive")
        if not asset.deposit_enabled:
            raise ValueError("Deposits are disabled for this asset")

        address_result = await db.execute(
            select(WalletAddress).where(
                WalletAddress.id == wallet_address_id,
                WalletAddress.asset_id == asset_id,
                WalletAddress.network == network,
                WalletAddress.status == "ACTIVE",
            )
        )
        wallet_address = address_result.scalar_one_or_none()
        if wallet_address is None:
            raise ValueError("Wallet address is not valid for this asset and network")

        wallet_result = await db.execute(
            select(Wallet).where(
                Wallet.id == wallet_address.wallet_id,
                Wallet.user_id == user_id,
            )
        )
        wallet = wallet_result.scalar_one_or_none()
        if wallet is None:
            raise ValueError("Wallet address does not belong to this user")

        duplicate_filter = [
            Deposit.network == network,
            Deposit.blockchain_tx_hash == blockchain_tx_hash,
        ]
        if blockchain_log_index is not None:
            duplicate_filter.append(
                Deposit.blockchain_log_index == blockchain_log_index
            )

        existing_result = await db.execute(
            select(Deposit).where(*duplicate_filter)
        )
        existing = existing_result.scalar_one_or_none()
        if existing is not None:
            if existing.user_id != user_id:
                raise ValueError(
                    "Blockchain transaction already belongs to another user"
                )
            return existing

        deposit = Deposit(
            user_id=user_id,
            wallet_address_id=wallet_address_id,
            asset_id=asset_id,
            network=network,
            blockchain_tx_hash=blockchain_tx_hash,
            blockchain_log_index=blockchain_log_index,
            amount=amount,
            confirmations=confirmations,
            status=(
                DepositService.CONFIRMED
                if confirmations > 0
                else DepositService.PENDING
            ),
        )

        try:
            async with db.begin_nested():
                db.add(deposit)
                await db.flush()
        except IntegrityError:
            existing_result = await db.execute(
                select(Deposit).where(*duplicate_filter)
            )
            existing = existing_result.scalar_one_or_none()
            if existing is None:
                raise ValueError("Blockchain transaction could not be created")
            if existing.user_id != user_id:
                raise ValueError(
                    "Blockchain transaction already belongs to another user"
                )
            return existing

        return deposit

    @staticmethod
    async def confirm_deposit(
        db: AsyncSession,
        *,
        deposit_id: UUID,
        confirmations: int,
    ) -> Deposit:
        """Update blockchain confirmations without crediting the balance."""

        if confirmations < 0:
            raise ValueError("Confirmations cannot be negative")

        result = await db.execute(
            select(Deposit).where(Deposit.id == deposit_id).with_for_update()
        )
        deposit = result.scalar_one_or_none()
        if deposit is None:
            raise ValueError("Deposit not found")
        if deposit.status == DepositService.CREDITED:
            return deposit
        if deposit.status == DepositService.FAILED:
            raise ValueError("Cannot confirm a failed deposit")
        if confirmations < deposit.confirmations:
            raise ValueError("Confirmation count cannot decrease")

        deposit.confirmations = confirmations
        deposit.status = (
            DepositService.CONFIRMED
            if confirmations > 0
            else DepositService.PENDING
        )
        await db.flush()
        return deposit

    @staticmethod
    async def credit_confirmed_deposit(
        db: AsyncSession,
        *,
        deposit_id: UUID,
    ) -> Deposit:
        """Credit a confirmed deposit exactly once."""

        deposit_result = await db.execute(
            select(Deposit).where(Deposit.id == deposit_id).with_for_update()
        )
        deposit = deposit_result.scalar_one_or_none()
        if deposit is None:
            raise ValueError("Deposit not found")
        if deposit.status == DepositService.CREDITED:
            return deposit
        if deposit.status != DepositService.CONFIRMED:
            raise ValueError("Deposit must be confirmed before crediting")

        treasury_result = await db.execute(
            select(Account)
            .where(
                Account.account_type == DepositService.SYSTEM_ACCOUNT_TYPE,
                Account.asset_id == deposit.asset_id,
            )
            .with_for_update()
        )
        treasury = treasury_result.scalar_one_or_none()
        if treasury is None:
            raise ValueError("System treasury account does not exist")

        customer_result = await db.execute(
            select(Account)
            .where(
                Account.user_id == deposit.user_id,
                Account.asset_id == deposit.asset_id,
                Account.account_type == DepositService.CUSTOMER_ACCOUNT_TYPE,
            )
            .with_for_update()
        )
        customer = customer_result.scalar_one_or_none()
        if customer is None:
            raise ValueError("Customer account does not exist")

        BalanceService._validate_account(treasury)
        BalanceService._validate_account(customer)

        await BalanceService.debit(treasury, deposit.amount)
        await BalanceService.credit(customer, deposit.amount)

        transaction = await LedgerService.create_transaction(
            db,
            transaction_type="DEPOSIT",
            entries=[
                {
                    "account_id": treasury.id,
                    "entry_type": "DEBIT",
                    "amount": deposit.amount,
                },
                {
                    "account_id": customer.id,
                    "entry_type": "CREDIT",
                    "amount": deposit.amount,
                },
            ],
            description=(
                f"Blockchain deposit {deposit.network}:"
                f"{deposit.blockchain_tx_hash}"
            ),
        )

        deposit.ledger_transaction_id = transaction.id
        deposit.status = DepositService.CREDITED
        await db.flush()
        return deposit
