import asyncio
import logging
import httpx

from eth_account import Account
from web3 import Web3
from eth_abi import encode

from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.services.withdrawal_service import WithdrawalService

logger = logging.getLogger(__name__)


class EthereumWithdrawalBroadcaster:

    POLL_INTERVAL = settings.ethereum_withdrawal_poll_seconds

    def __init__(self):
        # Ethereum JSON-RPC endpoint
        self.rpc_url = settings.ethereum_sepolia_rpc_url.strip()

        # Blockchain network
        self.network = settings.ethereum_sepolia_network.strip().upper()

        # BITNOVA ERC20 contract(checksum address)
        self.contract_address = Web3.to_checksum_address(
            settings.ethereum_sepolia_bitnova_contract.strip()
        )

        # Treasury wallet(checksum address)
        self.treasury_address = Web3.to_checksum_address(
            settings.ethereum_sepolia_treasury_address.strip()
        )

        self.private_key = (
            settings.ethereum_sepolia_treasury_private_key.strip()
        )

        # Sepolia chain id
        self.chain_id = settings.ethereum_sepolia_chain_id

    async def run_forever(self):
        logger.info("Ethereum withdrawal broadcaster started.")

        while True:
            try:
                await self.broadcast_once()
            except Exception:
                logger.exception("Withdrawal broadcaster iteration failed")

            await asyncio.sleep(self.POLL_INTERVAL)


    async def rpc_call(self, method: str, params: list):

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                self.rpc_url,
                json=payload,
            )

        response.raise_for_status()

        body = response.json()

        if body.get("error"):
            raise RuntimeError(body["error"])

        return body["result"]
    
    async def get_chain_id(self):
        result = await self.rpc_call("eth_chainId", [])
        return int(result, 16)

    async def get_latest_block(self):
        result = await self.rpc_call("eth_blockNumber", [])
        return int(result, 16)

    async def get_nonce(self):
        result = await self.rpc_call(
            "eth_getTransactionCount",
            [self.treasury_address, "pending"],
        )
        return int(result, 16)

    async def get_gas_price(self):
        result = await self.rpc_call("eth_gasPrice", [])
        return int(result, 16)

    def encode_transfer_data(
        self,
        recipient: str,
        amount: int,
    ) -> str:
        """
        ERC20 transfer(address,uint256)

        Function selector:
        a9059cbb
        """

        selector = "a9059cbb"

        recipient = Web3.to_checksum_address(recipient)

        encoded = encode(
            ["address", "uint256"],
            [recipient, amount],
        )

        return "0x" + selector + encoded.hex()

    async def estimate_gas(
        self,
        recipient: str,
        amount: int,
    ) -> int:

        data = self.encode_transfer_data(recipient, amount)

        result = await self.rpc_call(
            "eth_estimateGas",
            [
                {
                    "from": self.treasury_address,
                    "to": self.contract_address,
                    "data": data,
                }
            ],
        )

        return int(result, 16)

    async def build_transaction(
        self,
        recipient: str,
        amount: int,
    ) -> dict:

        nonce = await self.get_nonce()
        gas_price = await self.get_gas_price()
        gas_limit = await self.estimate_gas(recipient, amount)

        return {
            "chainId": self.chain_id,
            "nonce": nonce,
            "to": self.contract_address,
            "value": 0,
            "gas": gas_limit,
            "gasPrice": gas_price,
            "data": self.encode_transfer_data(recipient, amount),
        }

    async def sign_transaction(
        self,
        recipient: str,
        amount: int,
    ):

        transaction = await self.build_transaction(recipient, amount)

        signed = Account.sign_transaction(
            transaction,
            self.private_key,
        )

        return signed

    async def broadcast_transaction(
        self,
        recipient: str,
        amount: int,
    ) -> str:

        signed = await self.sign_transaction(recipient, amount)

        tx_hash = await self.rpc_call(
            "eth_sendRawTransaction",
            [signed.raw_transaction.hex()],
        )

        return tx_hash
    
    async def broadcast_once(self):

        async with AsyncSessionLocal() as db:

            stmt = (
                select(Withdrawal)
                .where(
                    Withdrawal.status == WithdrawalStatus.APPROVED.value
                )
                .with_for_update(skip_locked=True)
                .limit(1)
            )

            result = await db.execute(stmt)
            withdrawal = result.scalar_one_or_none()

            if withdrawal is None:
                await db.rollback()
                return

            # Prevent duplicate broadcast of the same withdrawal.
            if withdrawal.blockchain_tx_hash:
                logger.info(
                    "Withdrawal %s already has tx hash %s. Skipping.",
                    withdrawal.id,
                    withdrawal.blockchain_tx_hash,
                )
                await db.rollback()
                return
            try:
                await WithdrawalService.mark_broadcasting(
                    db=db,
                    withdrawal=withdrawal,
                )

            
                tx_hash = await self.broadcast_transaction(
                    withdrawal.destination_address,
                    int(withdrawal.amount * 1_000_000),   # BITNOVA has 6 decimals
                )

                await WithdrawalService.mark_broadcasted(
                    db=db,
                    withdrawal=withdrawal,
                    tx_hash=tx_hash,
                )

                await db.commit()

                logger.info(
                    "Withdrawal %s broadcasted. Tx=%s",
                    withdrawal.id,
                    tx_hash,
                )

            except Exception as exc:

                await db.rollback()

                withdrawal.status = WithdrawalService.mark_failed(
                    db=db,
                    withdrawal=withdrawal,
                    reason=str(exc),
                )
            
                await db.commit()

                logger.exception("Withdrawal broadcast failed"  )


async def main():
    broadcaster = EthereumWithdrawalBroadcaster()
    await broadcaster.run_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())        