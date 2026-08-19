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

export interface AccountBalance {
  id: string;
  asset_id: string;
  account_type: string;
  available_balance: number;
  locked_balance: number;
  total_balance: number;
  status: string;
}

export function getAccountBalances() {
  return apiClient<AccountBalance[]>("/accounts");
}