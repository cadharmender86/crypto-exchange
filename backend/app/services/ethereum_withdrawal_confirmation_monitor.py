import asyncio
import logging

from datetime import datetime, timezone

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.services.ethereum_withdrawal_broadcaster import (
    EthereumWithdrawalBroadcaster,
)

logger = logging.getLogger(__name__)


class EthereumWithdrawalConfirmationMonitor:

    POLL_INTERVAL = 15
    REQUIRED_CONFIRMATIONS = 3

    def __init__(self):
        self.rpc = EthereumWithdrawalBroadcaster()



    async def run_forever(self):
        logger.info("Withdrawal confirmation monitor started.")

        while True:
            try:
                await self.check_once()
            except Exception:
                logger.exception("Confirmation monitor failed")

            await asyncio.sleep(self.POLL_INTERVAL)

    async def check_once(self):

        async with AsyncSessionLocal() as db:

            result = await db.execute(
                select(Withdrawal).where(
                    Withdrawal.status == WithdrawalStatus.BROADCASTED.value
                )
            )

            withdrawals = result.scalars().all()

            logger.info("Found %s broadcasted withdrawals", len(withdrawals))

            latest_block = await self.rpc.get_latest_block()

            logger.info("Latest block: %s", latest_block)

            for withdrawal in withdrawals:

                receipt = await self.rpc.rpc_call(
                    "eth_getTransactionReceipt",
                    [withdrawal.blockchain_tx_hash],
                )

                # Transaction not mined yet.
                if receipt is None:
                    logger.info(
                        "Withdrawal %s receipt not found yet.",
                        withdrawal.id,
                    )
                    continue

                # Transaction was mined but reverted.
                if receipt["status"] == "0x0":

                    withdrawal.status = WithdrawalStatus.FAILED.value
                    withdrawal.failure_reason = "Blockchain transaction reverted"

                    logger.error(
                        "Withdrawal %s reverted on-chain.",
                        withdrawal.id,
    )

                    continue    
                    
                block_number = int(receipt["blockNumber"], 16)

                confirmations = latest_block - block_number + 1

                withdrawal.confirmations = confirmations

                logger.info(
                    "Withdrawal %s confirmations=%s",
                    withdrawal.id,
                    confirmations,
                )

                if confirmations >= self.REQUIRED_CONFIRMATIONS:

                    withdrawal.status = WithdrawalStatus.COMPLETED.value
                    withdrawal.completed_at = datetime.now(timezone.utc)

                    logger.info(
                        "Withdrawal %s COMPLETED.",
                        withdrawal.id,
                    )

            await db.commit()

async def main():
    monitor = EthereumWithdrawalConfirmationMonitor()
    await monitor.run_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())