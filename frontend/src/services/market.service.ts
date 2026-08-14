import { apiClient } from "./apiClient";

export function getMarketTicker() {
  return apiClient("/market/ticker");
}

export function getMarketAssets() {
  return apiClient("/market/assets");
}
