from bip_utils import (
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
)
from eth_utils import is_checksum_address, to_checksum_address

from app.blockchains.wallets.hd_wallet import HDWallet
from app.blockchains.wallets.provider import WalletProvider, WalletInfo


class EthereumWalletProvider(WalletProvider):

    network = "ETHEREUM_SEPOLIA"

    async def generate_wallet(self, index: int) -> WalletInfo:

        mnemonic = HDWallet.get_mnemonic()

        seed = Bip39SeedGenerator(mnemonic).Generate()

        wallet = (
            Bip44
            .FromSeed(seed, Bip44Coins.ETHEREUM)
            .Purpose()
            .Coin()
            .Account(0)
            .Change(Bip44Changes.CHAIN_EXT)
            .AddressIndex(index)
        )

        address = to_checksum_address(
            wallet.PublicKey().ToAddress()
        )

        return WalletInfo(
            address=address,
            public_key=wallet.PublicKey().RawCompressed().ToHex(),
            derivation_path=f"m/44'/60'/0'/0/{index}",
            index=index,
        )

    async def validate_address(self, address: str) -> bool:

        try:
            return is_checksum_address(address)
        except Exception:
            return False