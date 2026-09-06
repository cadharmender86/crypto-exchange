import asyncio
import logging
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.services.withdrawal_service import WithdrawalService
from app.services.ledger_service import LedgerService
from app.services.ethereum_withdrawal_broadcaster import (
    EthereumWithdrawalBroadcaster,
)

logger = logging.getLogger(__name__)


class EthereumWithdrawalConfirmationMonitor:

    POLL_INTERVAL = int(os.getenv("WITHDRAWAL_CONFIRMATION_POLL_INTERVAL", "15"))
    REQUIRED_CONFIRMATIONS = int(os.getenv("ETH_CONFIRMATIONS_REQUIRED", "1"))

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
                    Withdrawal.status == WithdrawalStatus.BROADCASTED.value,
                    Withdrawal.blockchain_tx_hash.is_not(None),
                    Withdrawal.network == "SEPOLIA"
                )
                .with_for_update(skip_locked=True)
                .limit(20)
            )

            withdrawals = result.scalars().all()

            logger.info("Found %s broadcasted withdrawals", len(withdrawals))

            latest_block = await self.rpc.get_latest_block()

            logger.info("Latest block: %s", latest_block)

            for withdrawal in withdrawals:

                withdrawal_id = withdrawal.id

                tx_hash = withdrawal.blockchain_tx_hash

                try:
                    await self.process_withdrawal(db, withdrawal)
                except Exception:
                    await db.rollback()
                    logger.exception(
                        "Failed confirmation processing for %s",
                        withdrawal_id,
                        tx_hash,
                    )    

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

                    await WithdrawalService.mark_failed(
                        db=db,
                        withdrawal=withdrawal,
                        reason="Blockchain transaction reverted",
                    )

                    if withdrawal.ledger_transaction_id:
                        await LedgerService.mark_failed(
                            db=db,
                            transaction_id=withdrawal.ledger_transaction_id,
                        )

                    logger.error(
                        "Withdrawal %s reverted on-chain.",
                        withdrawal.id,
                    )

                    continue    
                    
                block_number = int(receipt["blockNumber"], 16)

                confirmations = latest_block - block_number + 1

                withdrawal.confirmations = confirmations

                logger.info(
                    "CONFIRMATION | withdrawal=%s | tx=%s | confirmations=%s/%s",
                    withdrawal.id,
                    withdrawal.blockchain_tx_hash,
                    confirmations,
                    self.REQUIRED_CONFIRMATIONS,
                )

                if confirmations >= self.REQUIRED_CONFIRMATIONS:

                    await WithdrawalService.mark_completed(
                        db=db,
                        withdrawal=withdrawal,
                    )

                    await LedgerService.mark_posted(
                        db,
                        withdrawal.ledger_transaction_id,
                    )

                    logger.info(
                        "COMPLETED | withdrawal=%s | tx=%s",
                        withdrawal.id,
                        withdrawal.blockchain_tx_hash,
                    )

            await db.commit()

    async def process_withdrawal(
        self,
        db: AsyncSession,
        withdrawal: Withdrawal,
    ):

        receipt = await self.rpc.rpc_call(
            "eth_getTransactionReceipt",
            [withdrawal.blockchain_tx_hash],
        )

        if receipt is None:
            logger.info(
                "Waiting for receipt %s",
                withdrawal.blockchain_tx_hash,
            )
            return

        if receipt["status"] == "0x0":
            await WithdrawalService.mark_failed(
                db=db,
                withdrawal=withdrawal,
                reason="Blockchain transaction reverted",
            )

            if withdrawal.ledger_transaction_id:
                await LedgerService.mark_failed(
                    db=db,
                    transaction_id=withdrawal.ledger_transaction_id,
                )

            logger.error(
                "Withdrawal %s reverted on-chain.",
                withdrawal.id,
            )
            return

        latest_block = await self.rpc.get_latest_block()

        block_number = int(receipt["blockNumber"], 16)
        confirmations = latest_block - block_number + 1

        withdrawal.confirmations = confirmations
        await db.flush()

        logger.info(
            "CONFIRMATION | withdrawal=%s | confirmations=%s/%s",
            withdrawal.id,
            confirmations,
            self.REQUIRED_CONFIRMATIONS,
        )

        if confirmations < self.REQUIRED_CONFIRMATIONS:
            return

        await WithdrawalService.mark_completed(
            db=db,
            withdrawal=withdrawal,
        )

        if withdrawal.ledger_transaction_id:
            await LedgerService.mark_posted(
                db=db,
                transaction_id=withdrawal.ledger_transaction_id,
            )

        logger.info(
            "COMPLETED | withdrawal=%s",
            withdrawal.id,
        )        

async def main():
    monitor = EthereumWithdrawalConfirmationMonitor()
    await monitor.run_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())