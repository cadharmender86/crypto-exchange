import asyncio
import logging

from eth_utils import keccak
from decimal import Decimal
from web3 import Web3
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.blockchain_cursor import BlockchainCursor
from app.services.ethereum_withdrawal_broadcaster import (
    EthereumWithdrawalBroadcaster,
)
from app.models.wallet_address import WalletAddress
from app.models.asset import Asset
from app.services.deposit_service import DepositService

logger = logging.getLogger(__name__)


class EthereumDepositListener:

    NETWORK = "SEPOLIA"
    POLL_INTERVAL = 10

    TRANSFER_EVENT_TOPIC = Web3.keccak(
        text="Transfer(address,address,uint256)"
    ).hex()

    # SUPPORTED_TOKENS = {
    #     # Sepolia USDT (your deployed token)
    #     "0xYOUR_SEPOLIA_USDT_CONTRACT".lower(): {
    #         "symbol": "USDT",
    #         "decimals": 6,
    #     },

        # Later we'll add USDC, WETH...
    # }   

    def __init__(self):
        self.rpc = EthereumWithdrawalBroadcaster()

        # Loaded from database.
        self.supported_tokens = {}

    async def load_supported_tokens(self, db):

        result = await db.execute(
            select(Asset).where(
                Asset.contract_address.is_not(None),
                Asset.deposit_enabled.is_(True),
                Asset.is_active.is_(True),
            )
        )

        assets = result.scalars().all()

        self.supported_tokens = {
            asset.contract_address.lower(): {
                "asset_id": asset.id,
                "symbol": asset.symbol,
                "decimals": asset.decimal_places,
            }
            for asset in assets
        }

        logger.info(
            "Loaded %s ERC20 tokens.",
            len(self.supported_tokens),
        )

    async def run_forever(self):
        logger.info("Ethereum deposit listener started.")

        while True:
            try:
                await self.scan_once()
            except Exception:
                logger.exception("Deposit listener failed.")

            await asyncio.sleep(self.POLL_INTERVAL)

    async def scan_once(self):

        async with AsyncSessionLocal() as db:

            if not self.supported_tokens:
                await self.load_supported_tokens(db)

            cursor = await self.get_cursor(db)

            latest_block = await self.rpc.get_latest_block()

            if latest_block <= cursor.last_processed_block:
                logger.info(
                    "No new blocks. Cursor=%s Latest=%s",
                    cursor.last_processed_block,
                    latest_block,
                )
                return

            logger.info(
                "Scanning blocks %s → %s",
                cursor.last_processed_block + 1,
                latest_block,
            )

            for block_number in range(
                cursor.last_processed_block + 1,
                latest_block + 1,
            ):
                await self.scan_block(db, block_number)
                await self.save_cursor(db, cursor, block_number)

    async def get_cursor(self, db):
        result = await db.execute(
            select(BlockchainCursor).where(
                BlockchainCursor.network == self.NETWORK
            )
        )

        cursor = result.scalar_one_or_none()

        if cursor is None:
            latest_block = await self.rpc.get_latest_block()

            cursor = BlockchainCursor(
                network=self.NETWORK,
                last_processed_block=latest_block,
            )

            db.add(cursor)
            await db.commit()

            logger.info(
                "Initialized %s cursor at block %s",
                self.NETWORK,
                latest_block,
            )

        return cursor

    async def save_cursor(self, db, cursor, block_number):
        cursor.last_processed_block = block_number
        await db.commit()

    async def scan_block(self, db, block_number):

        block = await self.rpc.rpc_call(
            "eth_getBlockByNumber",
            [hex(block_number), False],   # don't fetch full tx objects
        )

        tx_count = len(block["transactions"])

        logger.info(
            "Block %s contains %s txs",
            block_number,
            tx_count,
        )

        # Scan ERC20 Transfer logs
        await self.process_block(db, block_number)

    async def process_block(self, db, block_number: int):
        receipt_logs = await self.rpc.rpc_call(
            "eth_getLogs",
            [{
                "fromBlock": hex(block_number),
                "toBlock": hex(block_number),
                "topics": [self.TRANSFER_EVENT_TOPIC],
            }],
        )

        logger.info(
            "Block %s transfer logs=%s",
            block_number,
            len(receipt_logs),
        )

        for log in receipt_logs:
            await self.process_transfer_log(db, log) 

    async def process_transfer_log(self, db, log):

        contract = log["address"].lower()

        token = self.supported_tokens.get(contract)

        if token is None:
            return

        # from_address = Web3.to_checksum_address(
        #     "0x" + log["topics"][1][-40:]
        # )

        to_address = Web3.to_checksum_address(
            "0x" + log["topics"][2][-40:]
        )

        amount_raw = int(log["data"], 16)

        amount = Decimal(amount_raw) / Decimal(10 ** token["decimals"])

        tx_hash = log["transactionHash"].lower()

        log_index = int(log["logIndex"], 16)

        logger.info(
            "TRANSFER detected token=%s amount=%s to=%s",
            token["symbol"],
            amount,
            to_address,
        )

        await self.match_wallet_and_create_deposit(
            db=db,
            recipient=to_address,
            tx_hash=tx_hash,
            log_index=log_index,
            block_number=int(log["blockNumber"], 16),
            amount=amount,
            contract=contract,
            token=token,
        )

    async def match_wallet_and_create_deposit(
        self,
        db,
        recipient: str,
        tx_hash: str,
        log_index: int,
        block_number: int,
        amount: Decimal,
        contract: str,
        token: dict[str, object],
    ):
        """
        Match recipient address with BitNova deposit wallets.
        Create a pending deposit if wallet belongs to a user.
        """

        wallet_result = await db.execute(
            select(WalletAddress).where(
                WalletAddress.network == self.NETWORK,
                WalletAddress.address == recipient.lower(),
            )
        )

        wallet = wallet_result.scalar_one_or_none()

        if wallet is None:
            return

        # asset_result = await db.execute(
        #     select(Asset).where(
        #         Asset.contract_address == contract
        #     )
        # )

        # asset = asset_result.scalar_one_or_none()

        asset_id = token["asset_id"]

        # if asset_id is None:
        #     logger.warning(
        #         "Asset not configured for contract %s",
        #         contract,
        #     )
        #     return

        deposit = await DepositService.create_detected_deposit(
            db=db,
            wallet_address=wallet,
            asset_id=asset_id,
            amount=amount,
            tx_hash=tx_hash,
            log_index=log_index,
            block_number=block_number,
        )

        await db.commit()

        logger.info(
            "DEPOSIT CREATED | user=%s | deposit=%s | %s %s",
            wallet.user_id,
            deposit.id,
            amount,
            token["symbol"],
        )               

async def main():
    listener = EthereumDepositListener()
    await listener.run_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())