"use client";

import { useEffect, useRef, useState } from "react";
import { getMarketCandleWebSocketUrl, getMarketCandles, MarketCandle } from "@/services/market.service";

const INTERVALS = [
  { label: "1m", value: "1m" },
  { label: "5m", value: "5m" },
  { label: "15m", value: "15m" },
  { label: "1H", value: "1h" },
  { label: "4H", value: "4h" },
  { label: "1D", value: "1d" },
];

const SUPPORTED_COINS = new Set(["BTC", "ETH", "SOL"]);

function formatPrice(value: number) {
  return value.toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

export default function CandlestickChart({ coin }: { coin: string }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const candlesRef = useRef<MarketCandle[]>([]);
  const [interval, setInterval] = useState("1m");
  const [loadedKey, setLoadedKey] = useState("");
  const [error, setError] = useState("");
  const [lastPrice, setLastPrice] = useState(0);
  const chartKey = `${coin}:${interval}`;
  const unsupported = !SUPPORTED_COINS.has(coin);
  const loading = !unsupported && loadedKey !== chartKey;
  const displayError = unsupported ? "Live chart is not available for this market yet." : error;

  useEffect(() => {
    let mounted = true;
    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined;

    if (unsupported) return () => undefined;

    candlesRef.current = [];
    const symbol = `${coin}USDT`;

    async function loadHistory() {
      setLastPrice(0);
      setError("");
      try {
        const history = await getMarketCandles(symbol, interval, 200);
        if (!mounted) return;
        candlesRef.current = history;
        setLastPrice(history.at(-1)?.close ?? 0);
      } catch (loadError) {
        console.error("Unable to load candle history:", loadError);
        if (mounted) setError("Unable to load chart data");
      } finally {
        if (mounted) setLoadedKey(chartKey);
      }
    }

    function connect() {
      if (!mounted) return;
      try {
        socket = new WebSocket(getMarketCandleWebSocketUrl(symbol, interval));
        socket.onmessage = (event) => {
          try {
            const candle = JSON.parse(event.data) as MarketCandle;
            if (!candle?.open_time) return;
            const current = candlesRef.current;
            const index = current.findIndex((item) => item.open_time === candle.open_time);
            if (index === -1) candlesRef.current = [...current.slice(-199), candle];
            else {
              const next = [...current];
              next[index] = candle;
              candlesRef.current = next;
            }
            setLastPrice(candle.close);
          } catch (socketError) {
            console.error("Invalid candle WebSocket message:", socketError);
          }
        };
        socket.onclose = () => {
          if (mounted) reconnectTimer = setTimeout(connect, 3000);
        };
        socket.onerror = () => socket?.close();
      } catch (socketError) {
        console.error("Unable to connect to candle feed:", socketError);
        reconnectTimer = setTimeout(connect, 3000);
      }
    }

    void loadHistory();
    reconnectTimer = setTimeout(connect, 0);

    return () => {
      mounted = false;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, [coin, interval, unsupported, chartKey]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const draw = () => {
      const rect = container.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const width = Math.max(320, rect.width);
      const height = Math.max(300, rect.height);
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = "#0b1118";
      ctx.fillRect(0, 0, width, height);

      const candles = candlesRef.current.slice(-100);
      if (!candles.length) return;
      const padding = { top: 18, right: 74, bottom: 30, left: 10 };
      const chartWidth = width - padding.left - padding.right;
      const chartHeight = height - padding.top - padding.bottom;
      const highs = candles.map((item) => item.high);
      const lows = candles.map((item) => item.low);
      const max = Math.max(...highs);
      const min = Math.min(...lows);
      const range = Math.max(max - min, max * 0.0001, 1);
      const scaleY = (value: number) => padding.top + ((max - value) / range) * chartHeight;

      ctx.font = "11px sans-serif";
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";
      for (let i = 0; i <= 4; i += 1) {
        const y = padding.top + (chartHeight / 4) * i;
        const price = max - (range / 4) * i;
        ctx.strokeStyle = "rgba(148,163,184,0.10)";
        ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(padding.left, y); ctx.lineTo(width - padding.right, y); ctx.stroke();
        ctx.fillStyle = "#64748b";
        ctx.fillText(`₹${formatPrice(price)}`, width - 8, y);
      }

      const candleSlot = chartWidth / candles.length;
      const bodyWidth = Math.max(2, candleSlot * 0.58);
      candles.forEach((candle) => {
        const x = padding.left + candleSlot * candles.indexOf(candle) + candleSlot / 2;
        const openY = scaleY(candle.open);
        const closeY = scaleY(candle.close);
        const highY = scaleY(candle.high);
        const lowY = scaleY(candle.low);
        const rising = candle.close >= candle.open;
        const color = rising ? "#10b981" : "#ef4444";
        ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(x, highY); ctx.lineTo(x, lowY); ctx.stroke();
        const bodyTop = Math.min(openY, closeY);
        const bodyHeight = Math.max(1, Math.abs(closeY - openY));
        ctx.fillRect(x - bodyWidth / 2, bodyTop, bodyWidth, bodyHeight);
      });

      const latest = candles.at(-1);
      if (latest) {
        const y = scaleY(latest.close);
        ctx.setLineDash([4, 4]); ctx.strokeStyle = "rgba(59,130,246,0.65)";
        ctx.beginPath(); ctx.moveTo(padding.left, y); ctx.lineTo(width - padding.right, y); ctx.stroke(); ctx.setLineDash([]);
      }
    };

    const observer = new ResizeObserver(draw);
    observer.observe(container);
    const timer = window.setInterval(draw, 1000);
    draw();
    return () => { observer.disconnect(); window.clearInterval(timer); };
  }, [coin, interval, lastPrice, loadedKey]);

  return (
    <div ref={containerRef} className="relative h-[390px] w-full overflow-hidden rounded-lg border border-white/[0.05] bg-[#0b1118]">
      <canvas ref={canvasRef} className="absolute inset-0" aria-label={`${coin}/INR candlestick chart`} />
      <div className="absolute left-3 top-3 z-10 flex items-center gap-2 text-[11px] text-slate-500"><span>Live {coin}/INR</span>{lastPrice > 0 && <span className="font-semibold text-slate-300">₹ {formatPrice(lastPrice)}</span>}</div>
      <div className="absolute right-3 top-2 z-10 flex rounded-lg border border-white/[0.06] bg-[#10161d]/90 p-1">
        {INTERVALS.map((item) => <button key={item.value} type="button" onClick={() => setInterval(item.value)} className={`rounded px-2 py-1 text-[10px] font-semibold ${interval === item.value ? "bg-blue-600 text-white" : "text-slate-500 hover:text-white"}`}>{item.label}</button>)}
      </div>
      {(loading || displayError) && <div className="absolute inset-0 z-20 flex items-center justify-center bg-[#0b1118]/80 text-sm text-slate-500">{loading ? "Loading live chart…" : displayError}</div>}
    </div>
  );
}
