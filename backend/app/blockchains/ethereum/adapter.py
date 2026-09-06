from decimal import Decimal

from app.blockchains.base import BlockchainAdapter
from app.services.ethereum_withdrawal_broadcaster import (
    EthereumWithdrawalBroadcaster,
)


class EthereumAdapter(BlockchainAdapter):
    network = "ETHEREUM_SEPOLIA"

    def __init__(self):
        self.rpc = EthereumWithdrawalBroadcaster()

    # Wallets
    async def generate_wallet(self, user_id: str):
        raise NotImplementedError()

    async def get_balance(self, address: str, asset: str):
        raise NotImplementedError()

    # Deposits
    async def scan_deposits(self, from_block: int, to_block: int):
        raise NotImplementedError()

    async def check_confirmations(self, tx_hash: str):
        return await self.rpc.get_confirmations(tx_hash)

    # Withdrawals
    async def broadcast_transaction(self, **kwargs):
        return await self.rpc.broadcast_transaction(**kwargs)

    async def estimate_fee(self, **kwargs) -> Decimal:
        raise NotImplementedError()

    # Generic RPC
    async def rpc_call(self, method, params):
        return await self.rpc.rpc_call(method, params)