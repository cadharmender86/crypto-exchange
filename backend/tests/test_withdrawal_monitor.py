import asyncio
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from decimal import Decimal
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.asset import Asset
from app.models.withdrawal import Withdrawal
from app.models.account import Account
from app.models.user import User
from app.services.blockchain.withdrawal_monitor import (
    EthereumWithdrawalMonitor,
)
from app.services.withdrawal_service import WithdrawalService


class FakeEthereumProvider:
    """Controlled provider for deterministic withdrawal tests."""

    network = "SEPOLIA"

    def __init__(
        self,
        *,
        receipt_status: str | None,
        confirmations: int | None,
    ) -> None:
        self.receipt_status = receipt_status
        self.confirmations = confirmations

    async def get_transaction_receipt(
        self,
        tx_hash: str,
    ):
        if self.receipt_status is None:
            return None

        return {
            "status": self.receipt_status,
        }

    async def get_confirmations(
        self,
        tx_hash: str,
    ):
        return self.confirmations


async def get_test_withdrawal(db):
    result = await db.execute(
        select(Withdrawal)
        .where(
            Withdrawal.user_id
            == select(Withdrawal.user_id)
            .limit(1)
            .scalar_subquery()
        )
        .order_by(Withdrawal.created_at.desc())
    )

    withdrawal = result.scalars().first()

    if withdrawal is None:
        raise AssertionError(
            "No withdrawal exists for monitor test"
        )

    return withdrawal


async def create_test_withdrawal(db):
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

    account_result = await db.execute(
        select(Account).where(
            Account.user_id == user.id,
            Account.asset_id == asset.id,
            Account.account_type == "CUSTOMER",
        )
    )
    account = account_result.scalar_one_or_none()

    if account is None:
        raise AssertionError(
            "User1 USDT customer account does not exist"
        )

    withdrawal = Withdrawal(
        user_id=user.id,
        account_id=account.id,
        asset_id=asset.id,
        network="SEPOLIA",
        destination_address=(
            "0x0000000000000000000000000000000000000001"
        ),
        amount=Decimal("1"),
        status="APPROVED",
        idempotency_key=(
            f"phase45-withdrawal-{uuid4().hex}"
        ),
        blockchain_tx_hash=(
            f"0xphase45-{uuid4().hex}"
        ),
    )

    db.add(withdrawal)
    await db.flush()

    return withdrawal

async def test_failed_transaction():
    async with AsyncSessionLocal() as db:
        withdrawal = await create_test_withdrawal(db)

        monitor = EthereumWithdrawalMonitor(
            FakeEthereumProvider(
                receipt_status="0x0",
                confirmations=None,
            )
        )

        result = await monitor.process_withdrawal(
            db,
            withdrawal.id,
        )

        if result.status != WithdrawalService.FAILED:
            raise AssertionError(
                f"Expected FAILED, got {result.status}"
            )

        await db.rollback()

    print("  PASS: failed transaction")


async def test_below_confirmation_threshold():
    async with AsyncSessionLocal() as db:
        withdrawal = await create_test_withdrawal(db)

        threshold = (
            settings.ethereum_withdrawal_confirmations
        )

        monitor = EthereumWithdrawalMonitor(
            FakeEthereumProvider(
                receipt_status="0x1",
                confirmations=threshold - 1,
            )
        )

        result = await monitor.process_withdrawal(
            db,
            withdrawal.id,
        )

        if result.status != "APPROVED":
            raise AssertionError(
                f"Expected APPROVED, got {result.status}"
            )

        await db.rollback()

    print("  PASS: below confirmation threshold")


async def test_at_confirmation_threshold():
    async with AsyncSessionLocal() as db:
        withdrawal = await create_test_withdrawal(db)

        threshold = (
            settings.ethereum_withdrawal_confirmations
        )

        monitor = EthereumWithdrawalMonitor(
            FakeEthereumProvider(
                receipt_status="0x1",
                confirmations=threshold,
            )
        )

        result = await monitor.process_withdrawal(
            db,
            withdrawal.id,
        )

        if result.status != WithdrawalService.COMPLETED:
            raise AssertionError(
                f"Expected COMPLETED, got {result.status}"
            )

        await db.rollback()

    print("  PASS: confirmation threshold reached")


async def test_unmined_transaction():
    async with AsyncSessionLocal() as db:
        withdrawal = await create_test_withdrawal(db)

        monitor = EthereumWithdrawalMonitor(
            FakeEthereumProvider(
                receipt_status=None,
                confirmations=None,
            )
        )

        result = await monitor.process_withdrawal(
            db,
            withdrawal.id,
        )

        if result.status != "APPROVED":
            raise AssertionError(
                f"Expected APPROVED, got {result.status}"
            )

        await db.rollback()

    print("  PASS: unmined transaction remains APPROVED")


async def main() -> None:
    print("=" * 70)
    print("BITNOVA WITHDRAWAL MONITOR TEST")
    print("=" * 70)

    threshold = (
        settings.ethereum_withdrawal_confirmations
    )

    print()
    print(
        f"Withdrawal confirmation threshold: {threshold}"
    )

    if threshold != 12:
        raise AssertionError(
            f"Expected threshold 12, got {threshold}"
        )

    await test_failed_transaction()
    await test_below_confirmation_threshold()
    await test_at_confirmation_threshold()
    await test_unmined_transaction()

    print()
    print("ALL WITHDRAWAL MONITOR TESTS PASSED")


if __name__ == "__main__":
    asyncio.run(main())