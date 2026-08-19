import { apiClient } from "./apiClient";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getApiOrigin(): string {
  return API_BASE_URL.replace(/\/api\/v1\/?$/, "");
}

export type MarketTicker = {
  symbol: string;
  price: number;
  last_price: number;
  price_usdt?: number;
  price_inr?: number;
  usdt_inr_rate?: number;
  quote_currency?: string;
  change_24h: number;
  high_24h?: number;
  low_24h?: number;
  volume_24h?: number;
  source?: string;
};

export type MarketAsset = {
  id: string;
  symbol: string;
  name: string;
  asset_type: string;
  decimal_places: number;
  is_active: boolean;
  deposit_enabled: boolean;
  withdrawal_enabled: boolean;
  trading_enabled: boolean;
};

export type MarketCandle = {
  symbol: string;
  interval: string;
  open_time: number;
  close_time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  quote_volume: number;
  closed: boolean;
  usdt_inr_rate: number;
  source: string;
};

export function getMarketAssets() {
  return apiClient<MarketAsset[]>("/assets");
}

export function getMarketTicker(): Promise<MarketTicker[]> {
  return apiClient<MarketTicker[]>("/market/tickers");
}

export function getMarketCandles(symbol: string, interval: string, limit = 200): Promise<MarketCandle[]> {
  return apiClient<MarketCandle[]>(
    `/market/candles?symbol=${encodeURIComponent(symbol)}&interval=${encodeURIComponent(interval)}&limit=${limit}`,
  );
}

export function getMarketWebSocketUrl(): string {
  return `${getApiOrigin().replace(/^http:/, "ws:").replace(/^https:/, "wss:")}/api/v1/market/ws`;
}

export function getMarketCandleWebSocketUrl(symbol: string, interval: string): string {
  return (
    `${getApiOrigin().replace(/^http:/, "ws:").replace(/^https:/, "wss:")}` +
    `/api/v1/market/ws/candles/${encodeURIComponent(symbol)}/${encodeURIComponent(interval)}`
  );
}
