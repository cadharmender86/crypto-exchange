from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "BitNova Exchange API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    api_v1_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+asyncpg://bitnova:bitnova_password"
        "@postgres:5432/bitnova"
    )

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

    # Market data provider configuration.
    # Provider endpoints are infrastructure settings and belong in the
    # environment. Business market membership and FX rates are migrated
    # separately into database configuration.
    binance_market_symbols: str = "btcusdt,ethusdt,solusdt"
    binance_market_intervals: str = "1m,5m,15m,1h,4h,1d"
    binance_ws_url: str = "wss://stream.binance.com:9443/stream"
    binance_kline_ws_url: str = "wss://stream.binance.com:9443/ws"
    binance_rest_url: str = "https://api.binance.com/api/v3/klines"

    @property
    def binance_market_intervals_set(self) -> set[str]:
        return {
            interval.strip().lower()
            for interval in self.binance_market_intervals.split(",")
            if interval.strip()
        }

    # Temporary controlled conversion used by the current market service.
    # This remains a transitional setting until the exchange-rate table is
    # implemented and the market service reads the active DB rate.
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

    cashfree_environment: str = "sandbox"
    cashfree_app_id: str = ""
    cashfree_secret_key: str = ""
    frontend_url: str = "http://localhost:3000"
    cashfree_api_base: str = "https://sandbox.cashfree.com/pg"
    cashfree_webhook_secret: str = ""
    cashfree_verify_webhook_signature: bool = True
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
