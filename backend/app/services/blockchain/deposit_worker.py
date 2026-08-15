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

                await asyncio.sleep(
                    self.poll_interval
                )

            except asyncio.CancelledError:
                break

            except Exception as exc:
                print(
                    f"Deposit worker error: {exc}"
                )

                await asyncio.sleep(
                    self.poll_interval
                )

    async def process_block(
        self,
        block_number: int,
    ) -> None:
        """Process all transactions in one block."""

        provider = self.monitor.provider

        block = await provider.get_block(
            block_number,
            full_transactions=True,
        )

        if not block:
            return

        transactions = block.get(
            "transactions",
            [],
        )

        for transaction in transactions:
            if not isinstance(transaction, dict):
                continue

            tx_hash = transaction.get("hash")

            if not tx_hash:
                continue

            tx_hash_lower = tx_hash.lower()

            if tx_hash_lower in (
                self._processed_transactions
            ):
                continue

            async with AsyncSessionLocal() as db:
                deposits = (
                    await self.monitor.process_transaction(
                        db,
                        tx_hash,
                    )
                )

                if deposits:
                    await db.commit()

                    print(
                        f"Processed deposit transaction "
                        f"{tx_hash}: "
                        f"{len(deposits)} deposit(s)"
                    )

            self._processed_transactions.add(
                tx_hash_lower
            )

    def stop(self) -> None:
        """Stop the worker loop."""

        self._running = False