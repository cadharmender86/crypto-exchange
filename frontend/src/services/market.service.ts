import { apiClient } from "./apiClient";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type MarketTicker = {
  symbol: string;
  price: number;
  last_price: number;
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

export function getMarketAssets() {
  return apiClient<MarketAsset[]>("/assets");
}

export function getMarketTicker(): Promise<MarketTicker[]> {
  return apiClient<MarketTicker[]>("/market/tickers");
}

export function getMarketWebSocketUrl(): string {
  return API_BASE_URL.replace(/^http:/, "ws:").replace(/^https:/, "wss:") + "/api/v1/market/ws";
}
