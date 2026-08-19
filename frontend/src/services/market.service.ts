import { apiClient } from "./apiClient";

export type MarketTicker = {
  symbol: string;
  price?: number;
  last_price?: number;
  change_24h?: number;
};

export type MarketAsset = {
  id: string;
  symbol: string;
  name: string;
  asset_type: string;
  decimal_places: number;
  is_active: boolean;
  // precision: number;
  // min_order_size: number;
  // max_order_size: number;
  // order_size_increment: number;
  // price_increment: number;
  deposit_enabled: boolean;
  withdrawal_enabled: boolean;
  trading_enabled: boolean;
};

export function getMarketAssets() {
  return apiClient<MarketAsset[]>("/assets");
}

/**
 * Market ticker API is not implemented by the current backend yet.
 * Return an empty list so dashboard consumers remain stable until the
 * market-data service/order-book integration is introduced.
 */
export function getMarketTicker(): Promise<MarketTicker[]> {
  return Promise.resolve([]);
}
