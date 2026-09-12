"""
BitNova Exchange Constants

Central location for enums shared across models, schemas,
services, repositories, and Alembic migrations.
"""

from enum import Enum


# =====================================================
# Exchange Settings
# =====================================================

class SettingValueType(str, Enum):
    STRING = "string"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    DECIMAL = "decimal"
    JSON = "json"


# =====================================================
# Order Engine
# =====================================================

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP_LIMIT"
    STOP_MARKET = "STOP_MARKET"


class TimeInForce(str, Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"


# =====================================================
# Trading Pair Status
# =====================================================

class TradingPairStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    SUSPENDED = "SUSPENDED"


# =====================================================
# Asset Types
# =====================================================

class AssetType(str, Enum):
    CRYPTO = "CRYPTO"
    FIAT = "FIAT"


# =====================================================
# Ledger Transaction Types
# =====================================================

class LedgerTransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRADE = "TRADE"
    TRADE_FEE = "TRADE_FEE"
    RESERVE = "RESERVE"
    RELEASE = "RELEASE"
    REFUND = "REFUND"