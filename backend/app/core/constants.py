"""
BitNova Business Constants

Central place for business enums/constants used across backend services.
Do NOT put environment variables or secrets here.
"""

# ==========================
# Wallet
# ==========================

class WalletType:
    CUSTOMER = "CUSTOMER"
    TREASURY = "TREASURY"


class WalletStatus:
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    SUSPENDED = "SUSPENDED"


# ==========================
# Assets
# ==========================

class AssetType:
    FIAT = "FIAT"
    CRYPTO = "CRYPTO"


class AssetStatus:
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"

# ==========================
# Trading
# ==========================

class TradingPairStatus:
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    MAINTENANCE = "MAINTENANCE"
    
# ==========================
# Exchange Settings
# ==========================

class SettingValueType:
    STRING = "string"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    DECIMAL = "decimal"
    JSON = "json"