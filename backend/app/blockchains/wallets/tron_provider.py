from app.blockchains.wallets.provider import WalletProvider, WalletInfo


class TronWalletProvider(WalletProvider):

    network = "TRON"

    async def generate_wallet(self, index: int) -> WalletInfo:
        raise NotImplementedError(
            "TRON HD wallet generation implemented in Phase 5.2.3"
        )

    async def validate_address(self, address: str) -> bool:

        return (
            address.startswith("T")
            and len(address) == 34
        )