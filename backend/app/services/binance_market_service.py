import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import websockets
from websockets.exceptions import ConnectionClosed

from app.core.config import settings

logger = logging.getLogger(__name__)

BINANCE_WS_URL = "wss://stream.binance.com:9443/stream"
DEFAULT_SYMBOLS = ("btcusdt", "ethusdt", "solusdt")


class BinanceMarketService:
    """Development/test market feed backed by Binance spot ticker streams."""

    def __init__(self, symbols: tuple[str, ...] = DEFAULT_SYMBOLS) -> None:
        self.symbols = tuple(symbol.lower() for symbol in symbols if symbol)
        self._latest: dict[str, dict[str, Any]] = {}
        self._subscribers: set[asyncio.Queue[dict[str, Any]]] = set()
        self._task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()

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

    async def _handle_message(self, raw_message: str | bytes) -> None:
        message = json.loads(raw_message)
        data = message.get("data", message)
        source_symbol = str(data.get("s", "")).upper()
        if not source_symbol:
            return

        usdt_price = float(data.get("c", 0))
        usdt_inr_rate = settings.market_usdt_inr_rate
        inr_price = usdt_price * usdt_inr_rate

        # Binance's ticker high/low are in the source quote currency (USDT).
        # Convert them as well so the synthetic INR ticker is internally consistent.
        high_usdt = float(data.get("h", 0))
        low_usdt = float(data.get("l", 0))
        high_inr = high_usdt * usdt_inr_rate
        low_inr = low_usdt * usdt_inr_rate

        # Binance volume is base-asset volume. It is valid to carry it across
        # the synthetic INR ticker unchanged because the base quantity is the same.
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

        for item in (usdt_item, inr_item):
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


binance_market_service = BinanceMarketService()
