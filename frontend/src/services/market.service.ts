import { apiClient } from "./apiClient";

export type MarketTicker = {
  symbol: string;
  price?: number;
  last_price?: number;
  change_24h?: number;
};

export function getMarketAssets() {
  return apiClient<any[]>("/assets");
}

/**
 * Market ticker API is not implemented by the current backend yet.
 * Return an empty list so dashboard consumers remain stable until the
 * market-data service/order-book integration is introduced.
 */
export function getMarketTicker(): Promise<MarketTicker[]> {
  return Promise.resolve([]);
}
