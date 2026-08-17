import asyncio

from app.core.database import AsyncSessionLocal
from app.services.blockchain.deposit_monitor import EthereumDepositMonitor
from app.services.blockchain.ethereum_provider import EthereumProvider


TX_HASH = "0x15dbca2fb3cbd2e1441e04d06e4837c1cd8649682b22afbdab89114fa2198eb9"


async def main():
    monitor = EthereumDepositMonitor(EthereumProvider())

    async with AsyncSessionLocal() as db:
        deposits = await monitor.process_transaction(
            db,
            TX_HASH,
        )

        print("Deposits:", deposits)

        await db.rollback()


if __name__ == "__main__":
    asyncio.run(main())
