from __future__ import annotations

import asyncio
import logging
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.asset import Asset
from app.models.deposit import Deposit
from app.models.wallet_address import WalletAddress
from app.services.deposit_service import DepositService

logger = logging.getLogger(__name__)

TRANSFER_TOPIC = (
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
)


class EthereumRpcError(RuntimeError):
    pass


class EthereumDepositMonitor:
    """Poll an EVM JSON-RPC endpoint for configured ERC-20 deposits.

    The monitor only discovers transfers and delegates settlement to
    DepositService. It never mutates balances directly.
    """

    def __init__(self):
        # Ethereum JSON-RPC endpoint
        self.rpc_url = settings.ethereum_sepolia_rpc_url.strip()

        # ERC20 token contract monitored for deposits
        self.contract_address = (
            settings.ethereum_sepolia_usdt_contract.strip().lower()
        )

        # Network metadata
        self.network = (
            settings.ethereum_sepolia_network.strip().upper()
        )
        self.asset_symbol = (
            settings.ethereum_sepolia_asset_symbol.strip().upper()
        )

        # Deposit monitor configuration
        self.required_confirmations = (settings.ethereum_deposit_required_confirmations)
        self.poll_seconds = settings.ethereum_deposit_poll_seconds
        self.lookback_blocks = settings.ethereum_deposit_lookback_blocks
        self.chunk_size = settings.ethereum_deposit_log_chunk_size
        
        if not self.rpc_url:
            raise ValueError("ETHEREUM_SEPOLIA_RPC_URL is required")
        if not self.contract_address:
            raise ValueError("ETHEREUM_SEPOLIA_USDT_CONTRACT is required")
        if not 1 <= self.required_confirmations:
            raise ValueError("ETHEREUM_DEPOSIT_REQUIRED_CONFIRMATIONS must be at least 1")
        if not 1 <= self.poll_seconds:
            raise ValueError("ETHEREUM_DEPOSIT_POLL_SECONDS must be at least 1")
        if not 1 <= self.lookback_blocks:
            raise ValueError("ETHEREUM_DEPOSIT_LOOKBACK_BLOCKS must be at least 1")
        if not 1 <= self.chunk_size:
            raise ValueError("ETHEREUM_DEPOSIT_LOG_CHUNK_SIZE must be at least 1")

    async def _rpc(
        self,
        client: httpx.AsyncClient,
        method: str,
        params: list[Any],
    ) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }

        logger.info("RPC REQUEST %s -> %s", method, payload)

        response = await client.post(self.rpc_url, json=payload)

        try:
            body = response.json()
        except Exception:
            body = response.text

        logger.info("RPC RESPONSE %s -> HTTP %s %s", method, response.status_code, body)

        if response.status_code != 200:
            raise EthereumRpcError(f"HTTP {response.status_code}: {body}")

        if isinstance(body, dict) and body.get("error"):
            raise EthereumRpcError(str(body["error"]))

        return body.get("result")

    async def latest_block(self, client: httpx.AsyncClient) -> int:
        result = await self._rpc(client, "eth_blockNumber", [])
        return int(result, 16)

    async def transfer_logs(
        self,
        client: httpx.AsyncClient,
        from_block: int,
        to_block: int,
        address_topics: list[str],
    ) -> list[dict[str, Any]]:
        if not address_topics:
            return []

        logs: list[dict[str, Any]] = []
        for start in range(from_block, to_block + 1, self.chunk_size):
            end = min(start + self.chunk_size - 1, to_block)
            result = await self._rpc(
                client,
                "eth_getLogs",
                [
                    {
                        "fromBlock": hex(start),
                        "toBlock": hex(end),
                        "address": self.contract_address,
                        "topics": [TRANSFER_TOPIC],
                    }
                ],
            )
            logs.extend(result or [])
        return logs

    async def receipt(
        self,
        client: httpx.AsyncClient,
        transaction_hash: str,
    ) -> dict[str, Any] | None:
        return await self._rpc(client, "eth_getTransactionReceipt", [transaction_hash])

    async def _wallet_addresses(self, db) -> list[WalletAddress]:
        result = await db.execute(
            select(WalletAddress)
            .join(Asset, Asset.id == WalletAddress.asset_id)
            .where(
                WalletAddress.network == self.network,
                WalletAddress.status == "ACTIVE",
                Asset.symbol == self.asset_symbol,
                Asset.is_active.is_(True),
                Asset.deposit_enabled.is_(True),
            )
        )
        return list(result.scalars().all())

    async def scan_once(self) -> None:
        async with AsyncSessionLocal() as db:
            wallet_addresses = await self._wallet_addresses(db)
            if not wallet_addresses:
                logger.info("No active %s deposit addresses configured", self.asset_symbol)
                return

            address_map = {
                address.address.lower(): address
                for address in wallet_addresses
                if address.address
            }
            topics = [
                "0x" + "0" * 24 + address[2:].lower()
                for address in address_map
                if address.startswith("0x") and len(address) == 42
            ]

            async with httpx.AsyncClient(timeout=20.0) as client:
                latest = await self.latest_block(client)
                from_block = max(0, latest - self.lookback_blocks + 1)
                logs = await self.transfer_logs(client, from_block, latest, topics)

                for log in logs:
                    await self._process_log(db, client, log, address_map, latest)

            await db.commit()

    async def _process_log(
        self,
        db,
        client: httpx.AsyncClient,
        log: dict[str, Any],
        address_map: dict[str, WalletAddress],
        latest_block: int,
    ) -> None:
        if log.get("removed"):
            return

        topics = log.get("topics") or []
        if len(topics) < 3:
            return
        to_topic = topics[2]
        if not isinstance(to_topic, str) or len(to_topic) !=66:
            return

        to_address = "0x" + to_topic[-40:]
        wallet_address = address_map.get(to_address.lower())
        if wallet_address is None:
            return

        transaction_hash = log.get("transactionHash")
        block_number_hex = log.get("blockNumber")
        log_index_hex = log.get("logIndex")
        data = log.get("data", "0x")
        if not transaction_hash or not block_number_hex or not log_index_hex or not data:
            return

        receipt = await self.receipt(client, transaction_hash)
        if not receipt or receipt.get("status") != "0x1":
            return

        raw_amount = int(data, 16)
        if raw_amount <= 0:
            return

        asset_result = await db.execute(
            select(Asset).where(Asset.id == wallet_address.asset_id)
        )
        asset = asset_result.scalar_one_or_none()
        if asset is None:
            return

        decimals = asset.decimal_places
        amount = Decimal(raw_amount) / (Decimal(10) ** decimals)
        block_number = int(block_number_hex, 16)
        log_index = int(log_index_hex, 16)
        confirmations = max(1, latest_block - block_number + 1)

        deposit = await DepositService.create_pending_deposit(
            db,
            user_id=await self._wallet_user_id(db, wallet_address),
            wallet_address_id=wallet_address.id,
            asset_id=wallet_address.asset_id,
            network=self.network,
            blockchain_tx_hash=transaction_hash,
            blockchain_log_index=log_index,
            amount=amount,
            confirmations=0,
        )

        await DepositService.confirm_deposit(
            db,
            deposit_id=deposit.id,
            confirmations=confirmations,
        )

        if confirmations >= self.required_confirmations:
            await DepositService.credit_confirmed_deposit(
                db,
                deposit_id=deposit.id,
            )

    async def _wallet_user_id(self, db, wallet_address: WalletAddress):
        from app.models.wallet import Wallet

        result = await db.execute(
            select(Wallet.user_id).where(Wallet.id == wallet_address.wallet_id)
        )
        user_id = result.scalar_one_or_none()
        if user_id is None:
            raise ValueError("Deposit wallet does not belong to a user")
        return user_id

    async def run_forever(self) -> None:
        logger.info(
            "Starting Ethereum deposit monitor network=%s confirmations=%s",
            self.network,
            self.required_confirmations,
        )
        while True:
            try:
                await self.scan_once()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Ethereum deposit monitor iteration failed")
            await asyncio.sleep(self.poll_seconds)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    monitor = EthereumDepositMonitor()
    await monitor.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
