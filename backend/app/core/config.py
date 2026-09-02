from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):

    app_name: str = "BitNova Exchange API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    api_v1_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+asyncpg://bitnova:bitnova_password"
        "@localhost:5432/bitnova"
    )

    # frontend_url: str = Field(
    #         default="http://localhost:3000",
    #         alias="FRONTEND_URL",
    # )

    redis_url: str = "redis://localhost:6379/0"

    cors_origins: str = "http://localhost:3000"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Login brute-force protection
    login_rate_limit_attempts: int = 5
    login_rate_limit_window_seconds: int = 60

    # Development-only endpoint protection. Keep this out of source control
    # and provide it through backend/.env.
    internal_test_deposit_key: str

    # Market-data configuration.
    # Binance supplies crypto/USDT prices; the backend converts them to INR.
    # Keep this configurable so the test environment can use a controlled
    # INR conversion without exposing pricing configuration to the browser.
    market_usdt_inr_rate: float = 88.0

    # Ethereum deposit monitoring. RPC URLs and token contracts are supplied
    # through backend/.env; secrets and provider credentials never belong in
    # source control.
    # ----------------------------------------------------
    # Ethereum / Sepolia (Shared Configuration)
    # ----------------------------------------------------

    ethereum_sepolia_rpc_url: str
    ethereum_sepolia_network: str = "ETHEREUM_SEPOLIA"
    ethereum_sepolia_chain_id: int = 11155111

    # ERC20 Contracts
    ethereum_sepolia_usdt_contract: str
    ethereum_sepolia_bitnova_contract: str

    # Asset symbols
    ethereum_sepolia_asset_symbol: str = "USDT"
    ethereum_sepolia_bitnova_asset_symbol: str = "BITNOVA"

    # Treasury wallet (used only by withdrawal broadcaster)
    ethereum_sepolia_treasury_address: str
    ethereum_sepolia_treasury_private_key: str

    # ----------------------------------------------------
    # Deposit Monitor Configuration
    # ----------------------------------------------------
    ethereum_deposit_required_confirmations: int = 3
    ethereum_deposit_poll_seconds: int = 10
    ethereum_deposit_lookback_blocks: int = 200
    ethereum_deposit_log_chunk_size: int = 50

    # ----------------------------------------------------
    # Withdrawal Broadcaster Configuration
    # ----------------------------------------------------
    ethereum_withdrawal_poll_seconds: int = 10
    ethereum_withdrawal_gas_limit: int = 60000
    ethereum_withdrawal_max_retries: int = 3

    # -----------------------------------------
    # Cashfree Payment Gateway
    # -----------------------------------------

    cashfree_environment: str = "sandbox"  # or "production"

    cashfree_app_id: str = ""

    cashfree_secret_key: str = ""

    frontend_url: str = "http://localhost:3000"

    cashfree_api_base: str = "https://sandbox.cashfree.com/pg"

    cashfree_webhook_secret: str = ""

    payment_order_expiry_minutes: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
