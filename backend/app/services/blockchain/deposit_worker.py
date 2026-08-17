import asyncio
from typing import Set

from app.core.database import AsyncSessionLocal
from app.services.blockchain.deposit_monitor import (
    EthereumDepositMonitor,
)


class EthereumDepositWorker:
    """Continuously scan new Ethereum blocks for deposits."""

    def __init__(
        self,
        monitor: EthereumDepositMonitor | None = None,
        poll_interval: float = 5.0,
    ) -> None:
        self.monitor = monitor or EthereumDepositMonitor()
        self.poll_interval = poll_interval
        self._running = False
        self._last_block: int | None = None
        self._processed_transactions: Set[str] = set()

    async def process_pending_deposits(self) -> None:
        """Advance pending deposits as blockchain confirmations increase."""

        from sqlalchemy import select

        from app.core.config import settings
        from app.models.deposit import Deposit
        from app.services.deposit_service import DepositService

        provider = self.monitor.provider

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Deposit)
                .where(
                    Deposit.network == provider.network,
                    Deposit.status == DepositService.PENDING,
                )
            )

            deposits = result.scalars().all()

            for deposit in deposits:
                confirmations = await provider.get_confirmations(
                    deposit.blockchain_tx_hash
                )

                if confirmations is None:
                    continue

                if confirmations < deposit.confirmations:
                    continue

                deposit = await DepositService.confirm_deposit(
                    db,
                    deposit_id=deposit.id,
                    confirmations=confirmations,
                    confirmation_threshold=(
                        settings.ethereum_deposit_confirmations
                    ),
                )

                if deposit.status == DepositService.CONFIRMED:
                    await DepositService.credit_confirmed_deposit(
                        db,
                        deposit_id=deposit.id,
                    )

            await db.commit()

    async def run(self) -> None:
        """Continuously scan new blocks."""

        self._running = True

        provider = self.monitor.provider

        while self._running:
            try:
                latest_block = (
                    await provider.get_block_number()
                )

                if self._last_block is None:
                    self._last_block = latest_block
                    print(
                        f"Deposit worker starting at block "
                        f"{latest_block}"
                    )

                while self._last_block < latest_block:
                    self._last_block += 1

                    await self.process_block(
                        self._last_block
                    )

                await self.process_pending_deposits
                await asyncio.sleep(
                    self.poll_interval
                )

            except asyncio.CancelledError:
                break

            except Exception:
                import traceback

                print("Deposit worker error:")
                traceback.print_exc()

                await asyncio.sleep(
                    self.poll_interval
                )

    async def process_block(
        self,
        block_number: int,
    ) -> None:
        """Process ERC-20 Transfer events in one block."""

        provider = self.monitor.provider

        logs = await provider.get_erc20_transfer_logs(
            from_block=block_number,
            to_block=block_number,
        )

        if not logs:
            return

        processed_transactions: set[str] = set()

        for log in logs:
            tx_hash = log.get("transactionHash")

            if not tx_hash:
                continue

            tx_hash_lower = tx_hash.lower()

            if tx_hash_lower in processed_transactions:
                continue

            processed_transactions.add(tx_hash_lower)

            async with AsyncSessionLocal() as db:
                deposits = await self.monitor.process_transaction(
                    db,
                    tx_hash,
                )

                if deposits:
                    await db.commit()

                    print(
                        f"Processed deposit transaction "
                        f"{tx_hash}: "
                        f"{len(deposits)} deposit(s)"
                    )

    def stop(self) -> None:
        """Stop the worker loop."""

        self._running = False
