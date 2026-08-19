import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx
import websockets
from websockets.exceptions import ConnectionClosed

from app.core.config import settings

logger = logging.getLogger(__name__)

BINANCE_WS_URL = "wss://stream.binance.com:9443/stream"
BINANCE_KLINE_WS_URL = "wss://stream.binance.com:9443/ws"
BINANCE_REST_URL = "https://api.binance.com/api/v3/klines"
DEFAULT_SYMBOLS = ("btcusdt", "ethusdt", "solusdt")
VALID_INTERVALS = {"1m", "5m", "15m", "1h", "4h", "1d"}


class BinanceMarketService:
    """Development/test market feed backed by Binance spot streams."""

    def __init__(self, symbols: tuple[str, ...] = DEFAULT_SYMBOLS) -> None:
        self.symbols = tuple(symbol.lower() for symbol in symbols if symbol)
        self._latest: dict[str, dict[str, Any]] = {}
        self._subscribers: set[asyncio.Queue[dict[str, Any]]] = set()
        self._task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()
        self._candle_tasks: dict[tuple[str, str], asyncio.Task[None]] = {}
        self._candle_latest: dict[tuple[str, str], dict[str, Any]] = {}
        self._candle_subscribers: dict[tuple[str, str], set[asyncio.Queue[dict[str, Any]]]] = {}

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stop.clear()
        self._task = asyncio.create_task(self._run(), name="binance-market-feed")

    async def stop(self) -> None:
        self._stop.set()

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        candle_tasks = list(self._candle_tasks.values())
        for task in candle_tasks:
            task.cancel()
        if candle_tasks:
            await asyncio.gather(*candle_tasks, return_exceptions=True)
        self._candle_tasks.clear()
        self._candle_subscribers.clear()
        self._candle_latest.clear()

    def snapshot(self) -> list[dict[str, Any]]:
        return list(self._latest.values())

    async def subscribe(self) -> AsyncIterator[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=20)
        self._subscribers.add(queue)
        try:
            for item in self.snapshot():
                yield item
            while not self._stop.is_set():
                yield await queue.get()
        finally:
            self._subscribers.discard(queue)

    async def history_candles(
        self,
        symbol: str,
        interval: str,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        normalized_symbol = self.normalize_symbol(symbol)
        normalized_interval = self.normalize_interval(interval)
        safe_limit = max(20, min(limit, 500))

        params = {
            "symbol": normalized_symbol,
            "interval": normalized_interval,
            "limit": safe_limit,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(BINANCE_REST_URL, params=params)
            response.raise_for_status()
            rows = response.json()

        rate = settings.market_usdt_inr_rate
        return [self._candle_from_binance_row(normalized_symbol, normalized_interval, row, rate) for row in rows]

    async def subscribe_candles(
        self,
        symbol: str,
        interval: str,
    ) -> AsyncIterator[dict[str, Any]]:
        normalized_symbol = self.normalize_symbol(symbol)
        normalized_interval = self.normalize_interval(interval)
        key = (normalized_symbol, normalized_interval)
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        subscribers = self._candle_subscribers.setdefault(key, set())
        subscribers.add(queue)

        task = self._candle_tasks.get(key)
        if not task or task.done():
            self._candle_tasks[key] = asyncio.create_task(
                self._run_candle_feed(normalized_symbol, normalized_interval),
                name=f"binance-kline-{normalized_symbol}-{normalized_interval}",
            )

        try:
            latest = self._candle_latest.get(key)
            if latest:
                yield latest
            while not self._stop.is_set():
                yield await queue.get()
        finally:
            subscribers.discard(queue)
            if not subscribers:
                self._candle_subscribers.pop(key, None)
                task = self._candle_tasks.pop(key, None)
                if task and not task.done():
                    task.cancel()

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        normalized = symbol.strip().upper()
        if normalized not in {symbol.upper() for symbol in DEFAULT_SYMBOLS}:
            raise ValueError("Unsupported market symbol")
        return normalized

    @staticmethod
    def normalize_interval(interval: str) -> str:
        normalized = interval.strip().lower()
        if normalized not in VALID_INTERVALS:
            raise ValueError("Unsupported candle interval")
        return normalized

    async def _run(self) -> None:
        streams = "/".join(f"{symbol}@ticker" for symbol in self.symbols)
        url = f"{BINANCE_WS_URL}?streams={streams}"

        while not self._stop.is_set():
            try:
                logger.info("Connecting to Binance market feed")
                async with websockets.connect(
                    url,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=5,
                ) as websocket:
                    logger.info("Connected to Binance market feed")
                    async for raw_message in websocket:
                        if self._stop.is_set():
                            break
                        await self._handle_message(raw_message)
            except (ConnectionClosed, OSError, asyncio.TimeoutError) as exc:
                logger.warning("Binance market feed disconnected: %s", exc)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Unexpected Binance market feed error")

            if not self._stop.is_set():
                await asyncio.sleep(3)

    async def _run_candle_feed(self, symbol: str, interval: str) -> None:
        stream_url = f"{BINANCE_KLINE_WS_URL}/{symbol.lower()}@kline_{interval}"
        key = (symbol, interval)

        while not self._stop.is_set() and self._candle_subscribers.get(key):
            try:
                logger.info("Connecting to Binance candle feed %s %s", symbol, interval)
                async with websockets.connect(
                    stream_url,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=5,
                ) as websocket:
                    async for raw_message in websocket:
                        if self._stop.is_set() or not self._candle_subscribers.get(key):
                            break
                        await self._handle_candle_message(symbol, interval, raw_message)
            except (ConnectionClosed, OSError, asyncio.TimeoutError) as exc:
                logger.warning("Binance candle feed disconnected %s %s: %s", symbol, interval, exc)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Unexpected Binance candle feed error for %s %s", symbol, interval)

            if not self._stop.is_set() and self._candle_subscribers.get(key):
                await asyncio.sleep(2)

    async def _handle_message(self, raw_message: str | bytes) -> None:
        message = json.loads(raw_message)
        data = message.get("data", message)
        source_symbol = str(data.get("s", "")).upper()
        if not source_symbol:
            return

        usdt_price = float(data.get("c", 0))
        usdt_inr_rate = settings.market_usdt_inr_rate
        inr_price = usdt_price * usdt_inr_rate
        high_usdt = float(data.get("h", 0))
        low_usdt = float(data.get("l", 0))
        high_inr = high_usdt * usdt_inr_rate
        low_inr = low_usdt * usdt_inr_rate
        base_volume = float(data.get("v", 0))

        common_usdt = {
            "price_usdt": usdt_price,
            "price_inr": inr_price,
            "usdt_inr_rate": usdt_inr_rate,
            "change_24h": float(data.get("P", 0)),
            "high_24h": high_usdt,
            "low_24h": low_usdt,
            "volume_24h": base_volume,
            "volume_currency": source_symbol.removesuffix("USDT"),
            "source": "BINANCE",
        }

        usdt_item = {
            "symbol": source_symbol,
            "price": usdt_price,
            "last_price": usdt_price,
            **common_usdt,
            "quote_currency": "USDT",
        }

        base_symbol = source_symbol.removesuffix("USDT")
        inr_symbol = f"{base_symbol}INR"
        inr_item = {
            "symbol": inr_symbol,
            "price": inr_price,
            "last_price": inr_price,
            "price_usdt": usdt_price,
            "price_inr": inr_price,
            "usdt_inr_rate": usdt_inr_rate,
            "quote_currency": "INR",
            "change_24h": float(data.get("P", 0)),
            "high_24h": high_inr,
            "low_24h": low_inr,
            "volume_24h": base_volume,
            "volume_currency": base_symbol,
            "source": "BINANCE+INR_RATE",
        }

        self._latest[source_symbol] = usdt_item
        self._latest[inr_symbol] = inr_item

        usdt_inr_item = {
            "symbol": "USDTINR",
            "price": usdt_inr_rate,
            "last_price": usdt_inr_rate,
            "price_usdt": 1.0,
            "price_inr": usdt_inr_rate,
            "usdt_inr_rate": usdt_inr_rate,
            "quote_currency": "INR",
            "change_24h": 0.0,
            "high_24h": usdt_inr_rate,
            "low_24h": usdt_inr_rate,
            "volume_24h": 0.0,
            "volume_currency": "USDT",
            "source": "CONFIGURED_USDT_INR_RATE",
        }
        self._latest["USDTINR"] = usdt_inr_item

        for item in (usdt_item, inr_item, usdt_inr_item):
            for queue in tuple(self._subscribers):
                if queue.full():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                try:
                    queue.put_nowait(item)
                except asyncio.QueueFull:
                    pass

    async def _handle_candle_message(self, symbol: str, interval: str, raw_message: str | bytes) -> None:
        message = json.loads(raw_message)
        data = message.get("k", {})
        if not data:
            return

        rate = settings.market_usdt_inr_rate
        candle = {
            "symbol": symbol,
            "interval": interval,
            "open_time": int(data.get("t", 0)),
            "close_time": int(data.get("T", 0)),
            "open": float(data.get("o", 0)) * rate,
            "high": float(data.get("h", 0)) * rate,
            "low": float(data.get("l", 0)) * rate,
            "close": float(data.get("c", 0)) * rate,
            "volume": float(data.get("v", 0)),
            "quote_volume": float(data.get("q", 0)) * rate,
            "closed": bool(data.get("x", False)),
            "usdt_inr_rate": rate,
            "source": "BINANCE+INR_RATE",
        }

        key = (symbol, interval)
        self._candle_latest[key] = candle
        for queue in tuple(self._candle_subscribers.get(key, ())):
            if queue.full():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            try:
                queue.put_nowait(candle)
            except asyncio.QueueFull:
                pass

    @staticmethod
    def _candle_from_binance_row(symbol: str, interval: str, row: list[Any], rate: float) -> dict[str, Any]:
        return {
            "symbol": symbol,
            "interval": interval,
            "open_time": int(row[0]),
            "close_time": int(row[6]),
            "open": float(row[1]) * rate,
            "high": float(row[2]) * rate,
            "low": float(row[3]) * rate,
            "close": float(row[4]) * rate,
            "volume": float(row[5]),
            "quote_volume": float(row[7]) * rate,
            "closed": True,
            "usdt_inr_rate": rate,
            "source": "BINANCE+INR_RATE",
        }


binance_market_service = BinanceMarketService()
