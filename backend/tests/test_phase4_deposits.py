import asyncio
import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.models.account import Account
from app.models.asset import Asset
from app.models.deposit import Deposit
from app.models.ledger_entry import LedgerEntry
from app.models.ledger_transaction import LedgerTransaction
from app.models.user import User
from app.models.wallet import Wallet
from app.models.wallet_address import WalletAddress
from app.services.deposit_service import DepositService


engine = create_async_engine(settings.database_url)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def test_valid_deposit_creation(db):
    print("\n[1] Valid deposit creation")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    wallet_result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )
    wallet = wallet_result.scalars().first()

    if wallet is None:
        raise AssertionError("User has no wallet")

    address_result = await db.execute(
        select(WalletAddress).where(
            WalletAddress.wallet_id == wallet.id,
            WalletAddress.asset_id == asset.id,
            WalletAddress.status == "ACTIVE",
        )
    )
    wallet_address = address_result.scalars().first()

    if wallet_address is None:
        raise AssertionError(
            "User has no active wallet address for USDT"
        )

    tx_hash = f"phase43-{uuid.uuid4().hex}"

    deposit = await DepositService.create_pending_deposit(
        db,
        user_id=user.id,
        wallet_address_id=wallet_address.id,
        asset_id=asset.id,
        network=wallet_address.network,
        blockchain_tx_hash=tx_hash,
        amount=Decimal("10"),
    )

    if deposit.status != DepositService.PENDING:
        raise AssertionError(
            f"Expected PENDING, got {deposit.status}"
        )

    if deposit.amount != Decimal("10"):
        raise AssertionError(
            f"Unexpected amount: {deposit.amount}"
        )

    await db.rollback()

    print("  PASS")


async def test_duplicate_deposit_is_idempotent(db):
    print("\n[2] Duplicate blockchain transaction is idempotent")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    wallet_result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )
    wallet = wallet_result.scalars().first()

    address_result = await db.execute(
        select(WalletAddress).where(
            WalletAddress.wallet_id == wallet.id,
            WalletAddress.asset_id == asset.id,
            WalletAddress.status == "ACTIVE",
        )
    )
    wallet_address = address_result.scalars().first()

    tx_hash = f"phase43-idempotent-{uuid.uuid4().hex}"

    first = await DepositService.create_pending_deposit(
        db,
        user_id=user.id,
        wallet_address_id=wallet_address.id,
        asset_id=asset.id,
        network=wallet_address.network,
        blockchain_tx_hash=tx_hash,
        amount=Decimal("25"),
    )

    await db.flush()

    second = await DepositService.create_pending_deposit(
        db,
        user_id=user.id,
        wallet_address_id=wallet_address.id,
        asset_id=asset.id,
        network=wallet_address.network,
        blockchain_tx_hash=tx_hash,
        amount=Decimal("25"),
    )

    if first.id != second.id:
        raise AssertionError(
            "Duplicate transaction created another deposit"
        )

    count = await db.scalar(
        select(
            __import__("sqlalchemy").func.count(Deposit.id)
        ).where(
            Deposit.network == wallet_address.network,
            Deposit.blockchain_tx_hash == tx_hash,
        )
    )

    if count != 1:
        raise AssertionError(
            f"Expected one deposit, found {count}"
        )

    await db.rollback()

    print("  PASS")


async def test_confirmation_progression(db):
    print("\n[3] Deposit confirmation progression")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    wallet_result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )
    wallet = wallet_result.scalars().first()

    address_result = await db.execute(
        select(WalletAddress).where(
            WalletAddress.wallet_id == wallet.id,
            WalletAddress.asset_id == asset.id,
            WalletAddress.status == "ACTIVE",
        )
    )
    wallet_address = address_result.scalars().first()

    deposit = await DepositService.create_pending_deposit(
        db,
        user_id=user.id,
        wallet_address_id=wallet_address.id,
        asset_id=asset.id,
        network=wallet_address.network,
        blockchain_tx_hash=f"phase43-confirm-{uuid.uuid4().hex}",
        amount=Decimal("15"),
    )

    deposit = await DepositService.confirm_deposit(
        db,
        deposit_id=deposit.id,
        confirmations=3,
    )

    if deposit.status != DepositService.CONFIRMED:
        raise AssertionError(
            f"Expected CONFIRMED, got {deposit.status}"
        )

    if deposit.confirmations != 3:
        raise AssertionError(
            f"Expected 3 confirmations, got "
            f"{deposit.confirmations}"
        )

    await db.rollback()

    print("  PASS")


async def test_unconfirmed_deposit_cannot_be_credited(db):
    print("\n[4] Unconfirmed deposit cannot be credited")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    wallet_result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )
    wallet = wallet_result.scalars().first()

    address_result = await db.execute(
        select(WalletAddress).where(
            WalletAddress.wallet_id == wallet.id,
            WalletAddress.asset_id == asset.id,
            WalletAddress.status == "ACTIVE",
        )
    )
    wallet_address = address_result.scalars().first()

    deposit = await DepositService.create_pending_deposit(
        db,
        user_id=user.id,
        wallet_address_id=wallet_address.id,
        asset_id=asset.id,
        network=wallet_address.network,
        blockchain_tx_hash=f"phase43-pending-{uuid.uuid4().hex}",
        amount=Decimal("20"),
    )

    try:
        await DepositService.credit_confirmed_deposit(
            db,
            deposit_id=deposit.id,
        )
    except ValueError as exc:
        if "confirmed" not in str(exc).lower():
            raise
    else:
        raise AssertionError(
            "Unconfirmed deposit was credited"
        )

    await db.rollback()

    print("  PASS")

async def test_confirmed_deposit_is_credited_exactly_once(db):
    print("\n[5] Confirmed deposit settlement and exactly-once credit")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    wallet_result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )
    wallet = wallet_result.scalars().first()

    if wallet is None:
        raise AssertionError("User has no wallet")

    address_result = await db.execute(
        select(WalletAddress).where(
            WalletAddress.wallet_id == wallet.id,
            WalletAddress.asset_id == asset.id,
            WalletAddress.status == "ACTIVE",
        )
    )
    wallet_address = address_result.scalars().first()

    if wallet_address is None:
        raise AssertionError(
            "User has no active wallet address"
        )

    # Locate customer account.
    customer_result = await db.execute(
        select(Account).where(
            Account.user_id == user.id,
            Account.asset_id == asset.id,
            Account.account_type == "CUSTOMER",
        )
    )
    customer = customer_result.scalar_one_or_none()

    if customer is None:
        raise AssertionError(
            "Customer account does not exist"
        )

    # Locate existing development treasury.
    treasury_result = await db.execute(
        select(Account).where(
            Account.asset_id == asset.id,
            Account.account_type == "SYSTEM_TREASURY",
        )
    )
    treasury = treasury_result.scalar_one_or_none()

    if treasury is None:
        raise AssertionError(
            "System treasury account does not exist"
        )

    amount = Decimal("10")

    customer_before = Decimal(
        str(customer.available_balance)
    )
    treasury_before = Decimal(
        str(treasury.available_balance)
    )

    if treasury_before < amount:
        raise AssertionError(
            "Treasury does not have enough balance for test"
        )

    deposit = await DepositService.create_pending_deposit(
        db,
        user_id=user.id,
        wallet_address_id=wallet_address.id,
        asset_id=asset.id,
        network=wallet_address.network,
        blockchain_tx_hash=(
            f"phase43-settlement-{uuid.uuid4().hex}"
        ),
        amount=amount,
    )

    await DepositService.confirm_deposit(
        db,
        deposit_id=deposit.id,
        confirmations=3,
    )

    credited = await DepositService.credit_confirmed_deposit(
        db,
        deposit_id=deposit.id,
    )

    if credited.status != DepositService.CREDITED:
        raise AssertionError(
            f"Expected CREDITED, got {credited.status}"
        )

    await db.refresh(customer)
    await db.refresh(treasury)

    customer_after = Decimal(
        str(customer.available_balance)
    )
    treasury_after = Decimal(
        str(treasury.available_balance)
    )

    if customer_after != customer_before + amount:
        raise AssertionError(
            f"Customer balance incorrect: "
            f"before={customer_before}, "
            f"after={customer_after}"
        )

    if treasury_after != treasury_before - amount:
        raise AssertionError(
            f"Treasury balance incorrect: "
            f"before={treasury_before}, "
            f"after={treasury_after}"
        )

    # Verify ledger transaction.
    if credited.ledger_transaction_id is None:
        raise AssertionError(
            "Credited deposit has no ledger transaction"
        )

    ledger_result = await db.execute(
        select(LedgerEntry).where(
            LedgerEntry.transaction_id
            == credited.ledger_transaction_id
        )
    )

    entries = list(ledger_result.scalars().all())

    if len(entries) != 2:
        raise AssertionError(
            f"Expected 2 ledger entries, got {len(entries)}"
        )

    debit_total = sum(
        (
            Decimal(str(entry.amount))
            for entry in entries
            if entry.entry_type == "DEBIT"
        ),
        Decimal("0"),
    )

    credit_total = sum(
        (
            Decimal(str(entry.amount))
            for entry in entries
            if entry.entry_type == "CREDIT"
        ),
        Decimal("0"),
    )

    if debit_total != amount:
        raise AssertionError(
            f"Unexpected debit total: {debit_total}"
        )

    if credit_total != amount:
        raise AssertionError(
            f"Unexpected credit total: {credit_total}"
        )

    if debit_total != credit_total:
        raise AssertionError(
            "Ledger transaction is not balanced"
        )

    # Exactly-once check.
    customer_before_retry = Decimal(
        str(customer_after)
    )

    ledger_count_before_retry = await db.scalar(
        select(func.count(LedgerEntry.id)).where(
            LedgerEntry.transaction_id
            == credited.ledger_transaction_id
        )
    )

    retry = await DepositService.credit_confirmed_deposit(
        db,
        deposit_id=deposit.id,
    )

    if retry.id != credited.id:
        raise AssertionError(
            "Retry returned a different deposit"
        )

    if retry.status != DepositService.CREDITED:
        raise AssertionError(
            "Retry changed deposit status"
        )

    await db.refresh(customer)

    customer_after_retry = Decimal(
        str(customer.available_balance)
    )

    if customer_after_retry != customer_before_retry:
        raise AssertionError(
            "Deposit was credited more than once"
        )

    ledger_count_after_retry = await db.scalar(
        select(func.count(LedgerEntry.id)).where(
            LedgerEntry.transaction_id
            == credited.ledger_transaction_id
        )
    )

    if ledger_count_after_retry != ledger_count_before_retry:
        raise AssertionError(
            "Retry created additional ledger entries"
        )

    await db.rollback()

    print("  PASS")

async def test_insufficient_treasury_does_not_credit_customer(db):
    print("\n[6] Insufficient treasury prevents customer credit")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    wallet_result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )
    wallet = wallet_result.scalars().first()

    if wallet is None:
        raise AssertionError("User has no wallet")

    address_result = await db.execute(
        select(WalletAddress).where(
            WalletAddress.wallet_id == wallet.id,
            WalletAddress.asset_id == asset.id,
            WalletAddress.status == "ACTIVE",
        )
    )
    wallet_address = address_result.scalars().first()

    if wallet_address is None:
        raise AssertionError(
            "User has no active wallet address"
        )

    customer_result = await db.execute(
        select(Account).where(
            Account.user_id == user.id,
            Account.asset_id == asset.id,
            Account.account_type == "CUSTOMER",
        )
    )
    customer = customer_result.scalar_one_or_none()

    if customer is None:
        raise AssertionError(
            "Customer account does not exist"
        )

    treasury_result = await db.execute(
        select(Account).where(
            Account.asset_id == asset.id,
            Account.account_type == "SYSTEM_TREASURY",
        )
    )
    treasury = treasury_result.scalar_one_or_none()

    if treasury is None:
        raise AssertionError(
            "System treasury account does not exist"
        )

    customer_before = Decimal(
        str(customer.available_balance)
    )
    treasury_before = Decimal(
        str(treasury.available_balance)
    )

    # Deliberately request more than the treasury can provide.
    amount = treasury_before + Decimal("1")

    deposit = await DepositService.create_pending_deposit(
        db,
        user_id=user.id,
        wallet_address_id=wallet_address.id,
        asset_id=asset.id,
        network=wallet_address.network,
        blockchain_tx_hash=(
            f"phase43-insufficient-"
            f"{uuid.uuid4().hex}"
        ),
        amount=amount,
    )

    await DepositService.confirm_deposit(
        db,
        deposit_id=deposit.id,
        confirmations=3,
    )

    try:
        await DepositService.credit_confirmed_deposit(
            db,
            deposit_id=deposit.id,
        )
    except ValueError as exc:
        if "insufficient" not in str(exc).lower():
            raise
    else:
        raise AssertionError(
            "Deposit was credited despite insufficient treasury"
        )

    await db.refresh(customer)
    await db.refresh(treasury)
    await db.refresh(deposit)

    customer_after = Decimal(
        str(customer.available_balance)
    )
    treasury_after = Decimal(
        str(treasury.available_balance)
    )

    if customer_after != customer_before:
        raise AssertionError(
            "Customer balance changed after failed settlement"
        )

    if treasury_after != treasury_before:
        raise AssertionError(
            "Treasury balance changed after failed settlement"
        )

    if deposit.status == DepositService.CREDITED:
        raise AssertionError(
            "Failed deposit became CREDITED"
        )

    if deposit.ledger_transaction_id is not None:
        raise AssertionError(
            "Failed settlement created a ledger transaction"
        )

    await db.rollback()

    print("  PASS")

async def test_confirmation_threshold_boundary(db):
    print("\n[7] Deposit confirmation threshold boundary")

    user_result = await db.execute(
        select(User).where(
            User.email == "user1@example.com"
        )
    )
    user = user_result.scalar_one()

    asset_result = await db.execute(
        select(Asset).where(
            Asset.symbol == "USDT"
        )
    )
    asset = asset_result.scalar_one()

    wallet_result = await db.execute(
        select(Wallet).where(
            Wallet.user_id == user.id
        )
    )
    wallet = wallet_result.scalars().first()

    address_result = await db.execute(
        select(WalletAddress).where(
            WalletAddress.wallet_id == wallet.id,
            WalletAddress.asset_id == asset.id,
            WalletAddress.status == "ACTIVE",
        )
    )
    wallet_address = address_result.scalars().first()

    threshold = settings.ethereum_deposit_confirmations

    below = await DepositService.create_pending_deposit(
        db,
        user_id=user.id,
        wallet_address_id=wallet_address.id,
        asset_id=asset.id,
        network=wallet_address.network,
        blockchain_tx_hash=f"phase45-below-{uuid.uuid4().hex}",
        amount=Decimal("1"),
        confirmations=threshold - 1,
        confirmation_threshold=threshold,
    )

    if below.status != DepositService.PENDING:
        raise AssertionError(
            f"Expected PENDING below threshold, got {below.status}"
        )

    at_threshold = await DepositService.create_pending_deposit(
        db,
        user_id=user.id,
        wallet_address_id=wallet_address.id,
        asset_id=asset.id,
        network=wallet_address.network,
        blockchain_tx_hash=f"phase45-threshold-{uuid.uuid4().hex}",
        amount=Decimal("1"),
        confirmations=threshold,
        confirmation_threshold=threshold,
    )

    if at_threshold.status != DepositService.CONFIRMED:
        raise AssertionError(
            f"Expected CONFIRMED at threshold, "
            f"got {at_threshold.status}"
        )

    await db.rollback()

    print("  PASS")

async def main():
    print("=" * 70)
    print("BITNOVA PHASE 4.3 DEPOSIT SERVICE TEST")
    print("=" * 70)

    async with SessionLocal() as db:
        await test_valid_deposit_creation(db)

    async with SessionLocal() as db:
        await test_duplicate_deposit_is_idempotent(db)

    async with SessionLocal() as db:
        await test_confirmation_progression(db)

    async with SessionLocal() as db:
        await test_unconfirmed_deposit_cannot_be_credited(db)

    async with SessionLocal() as db:
        await test_confirmed_deposit_is_credited_exactly_once(db)

    async with SessionLocal() as db:
        await test_insufficient_treasury_does_not_credit_customer(db)

    async with SessionLocal() as db:
        await test_confirmation_threshold_boundary(db)

    await engine.dispose()

    print("\n" + "=" * 70)
    print("PHASE 4.3 INITIAL SERVICE TESTS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
