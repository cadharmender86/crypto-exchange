from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any


class BlockchainAdapter(ABC):
    """
    Common interface implemented by every blockchain adapter.
    """

    network: str

    # Wallets
    @abstractmethod
    async def generate_wallet(self, user_id: str) -> dict:
        pass

    @abstractmethod
    async def get_balance(self, address: str, asset: str) -> Decimal:
        pass

    # Deposits
    @abstractmethod
    async def scan_deposits(self, from_block: int, to_block: int):
        pass

    @abstractmethod
    async def check_confirmations(self, tx_hash: str) -> int:
        pass

    # Withdrawals
    @abstractmethod
    async def broadcast_transaction(self, **kwargs) -> str:
        pass

    @abstractmethod
    async def estimate_fee(self, **kwargs) -> Decimal:
        pass

    # Generic RPC
    @abstractmethod
    async def rpc_call(self, method: str, params: list[Any]):
        pass