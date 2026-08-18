import { apiClient } from "./apiClient";

export interface WalletBalance {
  totalValue: number;
  available: number;
  locked: number;
  cryptoValue: number;
}

export function getWalletBalance() {
  return apiClient<WalletBalance>("/wallet/balance");
}

export function getWalletAssets() {
  return apiClient("/wallet/assets");
}