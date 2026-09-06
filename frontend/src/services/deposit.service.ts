import { apiClient } from "./apiClient";

export interface DepositAddress {
  asset_symbol: string;
  network: string;
  address: string;
  qr_code?: string;
}

export function getDepositAddress(asset: string) {
  return apiClient<DepositAddress>(
    `/deposits/address/${asset}`
  );
}