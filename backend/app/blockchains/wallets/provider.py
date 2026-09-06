from abc import ABC, abstractmethod
from typing import TypedDict


class WalletInfo(TypedDict):
    address: str
    public_key: str
    derivation_path: str
    index: int


class WalletProvider(ABC):
    """
    Common interface implemented by every blockchain wallet provider.
    """

    network: str

    @abstractmethod
    async def generate_wallet(
        self,
        index: int,
    ) -> WalletInfo:
        """
        Generate deterministic wallet at derivation index.
        """

    @abstractmethod
    async def validate_address(
        self,
        address: str,
    ) -> bool:
        """
        Validate blockchain address format.
        """