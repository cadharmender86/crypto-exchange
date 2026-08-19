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
        "@localhost:5432/bitnova"
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

    # Market-data configuration.
    # Binance supplies crypto/USDT prices; the backend converts them to INR.
    # Keep this configurable so the test environment can use a controlled
    # INR conversion without exposing pricing configuration to the browser.
    market_usdt_inr_rate: float = 88.0

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
