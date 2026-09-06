import os
from functools import lru_cache


class HDWallet:

    """
    Master seed manager.
    Currently reads seed phrase from environment.
    Encryption/KMS comes in Phase 5.2.4.
    """

    @staticmethod
    @lru_cache
    def get_mnemonic() -> str:

        mnemonic = os.getenv("HD_WALLET_MNEMONIC")

        if not mnemonic:
            raise RuntimeError(
                "HD_WALLET_MNEMONIC environment variable is missing."
            )

        return mnemonic.strip()