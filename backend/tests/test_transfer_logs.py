import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncio

from app.services.blockchain.ethereum_provider import (
    EthereumProvider,
)


BLOCK_NUMBER = 11499244

TRANSFER_TOPIC = (
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4"
    "a11628f55a4df523b3ef"
)


async def main():
    provider = EthereumProvider()

    logs = await provider.get_logs(
        from_block=BLOCK_NUMBER,
        to_block=BLOCK_NUMBER,
        topics=[TRANSFER_TOPIC],
    )

    print("Network:", provider.network)
    print("Block:", BLOCK_NUMBER)
    print("Transfer logs:", len(logs))

    for log in logs:
        print()
        print("Transaction:", log.get("transactionHash"))
        print("Token:", log.get("address"))
        print("Log index:", log.get("logIndex"))

    target = [
        log
        for log in logs
        if (
            log.get("transactionHash", "").lower()
            == "0x7be4400e67f84145bf13f288a9d49b6206bdcb39b8d418b52a9f1a91dc815050"
        )
    ]

    print()
    print("Target transaction logs:", len(target))

    if len(target) == 0:
        raise AssertionError(
            "Fresh deposit transaction was not found"
        )

    print("Fresh deposit transaction FOUND")


if __name__ == "__main__":
    asyncio.run(main())