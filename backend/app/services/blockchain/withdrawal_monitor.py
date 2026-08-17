from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.blockchain.ethereum_provider import EthereumProvider
from app.services.withdrawal_service import WithdrawalService
from app.core.config import settings


class EthereumWithdrawalMonitor:
    """Monitor Ethereum withdrawal transactions."""

    def __init__(
        self,
        provider: EthereumProvider | None = None,
    ) -> None:
        self.provider = provider or EthereumProvider()

    async def process_withdrawal(
        self,
        db: AsyncSession,
        withdrawal_id: Any,
    ):
        """Process one withdrawal's blockchain transaction."""

        from sqlalchemy import select

        from app.models.withdrawal import Withdrawal

        result = await db.execute(
            select(Withdrawal)
            .where(Withdrawal.id == withdrawal_id)
            .with_for_update()
        )

        withdrawal = result.scalar_one_or_none()

        if withdrawal is None:
            raise ValueError("Withdrawal not found")

        if withdrawal.blockchain_tx_hash is None:
            return withdrawal

        if withdrawal.status == WithdrawalService.FAILED:
            return withdrawal

        receipt = await self.provider.get_transaction_receipt(
            withdrawal.blockchain_tx_hash
        )

        if receipt is None:
            return withdrawal

        receipt_status = receipt.get("status")

        if receipt_status == "0x0":
            withdrawal.status = WithdrawalService.FAILED
            await db.flush()
            return withdrawal

        if receipt_status == "0x1":
            confirmations = await self.provider.get_confirmations(
                withdrawal.blockchain_tx_hash
            )

            if confirmations is None:
                return withdrawal

            if (
                confirmations
                >= settings.ethereum_withdrawal_confirmations
            ):
                withdrawal.status = WithdrawalService.COMPLETED
                await db.flush()
            return withdrawal


        return withdrawal