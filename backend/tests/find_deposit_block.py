import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncio

from app.services.blockchain.ethereum_provider import (
    EthereumProvider,
)


TX_HASH = (
    "0x7be4400e67f84145bf13f288a9d49b6206bdcb39b8d418b52a9f1a91dc815050"
)


async def main():
    provider = EthereumProvider()

    transaction = await provider.get_transaction(TX_HASH)

    if transaction is None:
        print("Transaction not found")
        return

    block_number = int(
        transaction["blockNumber"],
        16,
    )

    print("Network:", provider.network)
    print("Transaction:", TX_HASH)
    print("Block number:", block_number)
    print(
        "Transaction index:",
        int(transaction["transactionIndex"], 16),
    )


if __name__ == "__main__":
    asyncio.run(main())