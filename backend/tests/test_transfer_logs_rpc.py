import asyncio

from app.services.blockchain.ethereum_provider import EthereumProvider


async def main():
    provider = EthereumProvider()

    logs = await provider.get_erc20_transfer_logs(
        from_block=11501084,
        to_block=11501084,
    )

    print("Transfer logs:", len(logs))

    for log in logs:
        print(
            "TX:",
            log.get("transactionHash"),
            "TOKEN:",
            log.get("address"),
            "LOG:",
            log.get("logIndex"),
        )


if __name__ == "__main__":
    asyncio.run(main())
