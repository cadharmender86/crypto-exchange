# from pydoc_data.topics import topics
#from curses import raw
from typing import Any
#from unittest import result

import httpx

from app.core.config import settings
# from backend.app.api.v1 import transfers


class EthereumProvider:
    """Minimal Ethereum JSON-RPC provider for testnet monitoring."""

    def __init__(self) -> None:
        self.network = settings.ethereum_network
        self.api_key = settings.alchemy_api_key
        self.rpc_url = (
            f"https://eth-{self.network}.g.alchemy.com/v2/{self.api_key}"
        )

    async def _rpc(
        self,
        method: str,
        params: list[Any] | None = None,
    ) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or [],
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                self.rpc_url,
                json=payload,
            )

        response.raise_for_status()

        data = response.json()

        if "error" in data:
            raise RuntimeError(
                f"Ethereum RPC error: {data['error']}"
            )

        return data["result"]

    async def get_block_number(self) -> int:
        """Return the latest Ethereum block number."""
        result = await self._rpc("eth_blockNumber")
        return int(result, 16)

    async def get_block(
        self,
        block_number: int,
        *,
        full_transactions: bool = True,
    ) -> dict[str, Any]:
        """Return an Ethereum block by number."""

        return await self._rpc(
            "eth_getBlockByNumber",
            [
                hex(block_number),
                full_transactions,
            ],
        )
    async def get_transaction(self, tx_hash: str) -> dict[str, Any] | None:
        """Return transaction data by hash."""
        return await self._rpc(
            "eth_getTransactionByHash",
            [tx_hash],
        )

    async def get_transaction_receipt(
        self,
        tx_hash: str,
    ) -> dict[str, Any] | None:
        """Return transaction receipt by hash."""
        return await self._rpc(
            "eth_getTransactionReceipt",
            [tx_hash],
        )

    async def get_confirmations(self, tx_hash: str) -> int | None:
        """Return the number of confirmations for a transaction.

        Returns None when the transaction is not mined yet.
        """
        transaction = await self.get_transaction(tx_hash)

        if transaction is None:
            return None

        block_number_hex = transaction.get("blockNumber")

        if block_number_hex is None:
            return 0

        transaction_block = int(block_number_hex, 16)
        current_block = await self.get_block_number()

        return max(current_block - transaction_block + 1, 0)

    async def get_erc20_transfer_events(
    self,
    tx_hash: str,
    ) -> list[dict[str, Any]]:
        """Extract ERC-20 Transfer events from a transaction receipt."""

        receipt = await self.get_transaction_receipt(tx_hash)

        if receipt is None:
            return []

        transfer_topic = (
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4"
            "a11628f55a4df523b3ef"
        )

        transfers = []

        for log in receipt.get("logs", []):
            topics = log.get("topics", [])

            if len(topics) < 3:
                continue

            if topics[0].lower() != transfer_topic:
                continue

            from_address = "0x" + topics[1][-40:]
            to_address = "0x" + topics[2][-40:]

            data = log.get("data", "0x")

            if not data or data == "0x":
                continue

            amount = int(data, 16)

            transfers.append(
            {
                "token_address": log.get("address"),
                "from": from_address,
                "to": to_address,
                "amount": amount,
                "log_index": int(
                    log.get("logIndex", "0x0"),
                    16,
                ),
            }
        )

        return transfers

    async def get_erc20_decimals(self, token_address: str) -> int:
        """Return ERC-20 token decimals."""

        data = "0x313ce567"

        result = await self._rpc(
            "eth_call",
            [
                {
                    "to": token_address,
                    "data": data,
                },
                "latest",
            ],
        )
        return int(result, 16)


    async def get_erc20_symbol(self, token_address: str) -> str:
        """Return ERC-20 token symbol."""

        data = "0x95d89b41"

        result = await self._rpc(
            "eth_call",
            [
                {
                    "to": token_address,
                    "data": data,
                },
                "latest",
            ],
        )


        raw = bytes.fromhex(result[2:])

        # Standard ABI string response:
        # offset + length + UTF-8 bytes
        if len(raw) >= 64:
            length = int.from_bytes(raw[32:64], "big")
            if length > 0 and 64 + length <= len(raw):
                return raw[64:64 + length].decode(
                    "utf-8",
                    errors="replace",
                )

            return ""
