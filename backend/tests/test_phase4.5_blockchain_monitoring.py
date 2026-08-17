import asyncio
import sys
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.asset import Asset
from app.models.deposit import Deposit
from app.models.user import User
from app.models.wallet import Wallet
from app.models.wallet_address import WalletAddress
from app.services.blockchain.deposit_monitor import EthereumDepositMonitor
from app.services.blockchain.deposit_worker import EthereumDepositWorker
from app.services.deposit_service import DepositService


class FakeEthereumProvider:
    """Controlled provider for deterministic worker tests."""

    network = "SEPOLIA"

    def __init__(self, confirmations: int) -> None:
        self.confirmations = confirmations

    async def get_confirmations(
        self,
        tx_hash: str,
    ) -> int:
        return self.confirmations


async def get_test_wallet_data(db):
    user = (
        await db.execute(
            select(User).where(
                User.email == "user1@example.com"
            )
        )
    ).scalar_one()

    asset = (
        await db.execute(
            select(Asset).where(
                Asset.symbol == "USDT"
            )
        )
    ).scalar_one()

    wallet = (
        await db.execute(
            select(Wallet).where(
                Wallet.user_id == user.id
            )
        )
    ).scalars().first()

    if wallet is None:
        raise AssertionError("Test wallet not found")

    wallet_address = (
        await db.execute(
            select(WalletAddress).where(
                WalletAddress.wallet_id == wallet.id,
                WalletAddress.asset_id == asset.id,
                WalletAddress.network == "SEPOLIA",
                WalletAddress.status == "ACTIVE",
            )
        )
    ).scalars().first()

    if wallet_address is None:
        raise AssertionError(
            "Active test wallet address not found"
        )

    return user, asset, wallet, wallet_address


async def main() -> None:
    print("=" * 70)
    print("BITNOVA PHASE 4.5 BLOCKCHAIN MONITORING TEST")
    print("=" * 70)

    threshold = settings.ethereum_deposit_confirmations

    print()
    print(
        f"Confirmation threshold: {threshold}"
    )

    if threshold != 12:
        raise AssertionError(
            f"Expected threshold 12, got {threshold}"
        )

    # ------------------------------------------------------------
    # Create a controlled pending deposit
    # ------------------------------------------------------------

    async with AsyncSessionLocal() as db:
        (
            user,
            asset,
            wallet,
            wallet_address,
        ) = await get_test_wallet_data(db)

        tx_hash = (
            f"phase45-worker-{uuid4().hex}"
        )

        deposit = (
            await DepositService.create_pending_deposit(
                db,
                user_id=user.id,
                wallet_address_id=wallet_address.id,
                asset_id=asset.id,
                network="SEPOLIA",
                blockchain_tx_hash=tx_hash,
                amount=Decimal("1"),
                confirmations=11,
                confirmation_threshold=threshold,
            )
        )

        if deposit.status != DepositService.PENDING:
            raise AssertionError(
                f"Expected PENDING, got {deposit.status}"
            )

        await db.commit()

        print()
        print("[1] Created deposit at 11 confirmations")
        print("  PASS")

    # ------------------------------------------------------------
    # 11 confirmations must remain PENDING
    # ------------------------------------------------------------

    worker = EthereumDepositWorker(
        monitor=EthereumDepositMonitor(
            provider=FakeEthereumProvider(
                confirmations=11
            )
        )
    )

    await worker.process_pending_deposits()

    async with AsyncSessionLocal() as db:
        deposit = (
            await db.execute(
                select(Deposit).where(
                    Deposit.blockchain_tx_hash == tx_hash
                )
            )
        ).scalar_one()

        if deposit.confirmations != 11:
            raise AssertionError(
                f"Expected 11 confirmations, "
                f"got {deposit.confirmations}"
            )

        if deposit.status != DepositService.PENDING:
            raise AssertionError(
                f"Expected PENDING, "
                f"got {deposit.status}"
            )

        print("[2] 11 confirmations remain PENDING")
        print("  PASS")

    # ------------------------------------------------------------
    # 12 confirmations must confirm and credit
    # ------------------------------------------------------------

    worker.monitor.provider = FakeEthereumProvider(
        confirmations=12
    )

    await worker.process_pending_deposits()

    async with AsyncSessionLocal() as db:
        deposit = (
            await db.execute(
                select(Deposit).where(
                    Deposit.blockchain_tx_hash == tx_hash
                )
            )
        ).scalar_one()

        if deposit.confirmations != 12:
            raise AssertionError(
                f"Expected 12 confirmations, "
                f"got {deposit.confirmations}"
            )

        if deposit.status != DepositService.CREDITED:
            raise AssertionError(
                f"Expected CREDITED, "
                f"got {deposit.status}"
            )

        if deposit.ledger_transaction_id is None:
            raise AssertionError(
                "Expected ledger transaction ID"
            )

        print(
            "[3] 12 confirmations → CONFIRMED → CREDITED"
        )
        print("  PASS")

    # ------------------------------------------------------------
    # Running scanner again must not duplicate credit
    # ------------------------------------------------------------

    await worker.process_pending_deposits()

    async with AsyncSessionLocal() as db:
        deposit = (
            await db.execute(
                select(Deposit).where(
                    Deposit.blockchain_tx_hash == tx_hash
                )
            )
        ).scalar_one()

        if deposit.status != DepositService.CREDITED:
            raise AssertionError(
                f"Expected CREDITED after repeat scan, "
                f"got {deposit.status}"
            )

        print(
            "[4] Repeated scanner remains CREDITED"
        )
        print("  PASS")

    print()
    print("=" * 70)
    print("PHASE 4.5.2 CONFIRMATION SCANNER TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())