from app.blockchains.ethereum.adapter import EthereumAdapter


class BlockchainManager:
    """
    Returns the correct blockchain adapter for a network.
    """

    _services = {
        "ETHEREUM": EthereumAdapter(),
        "ETHEREUM_SEPOLIA": EthereumAdapter(),

        # Future phases
        # "TRON": TronAdapter(),
        # "TRON_NILE": TronAdapter(),
        # "BSC": BSCAdapter(),
    }

    @classmethod
    def get_service(cls, network: str):
        service = cls._services.get(network)

        if service is None:
            raise ValueError(
                f"Unsupported blockchain network: {network}"
            )

        return service