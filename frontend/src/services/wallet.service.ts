import { apiClient } from "./apiClient";

function hasAccessToken() {
  if (typeof window === "undefined") return false;

  const token = localStorage.getItem("bitnova_access_token");
  if (!token) return false;

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    if (typeof payload?.exp === "number" && payload.exp <= Math.floor(Date.now() / 1000)) {
      localStorage.removeItem("bitnova_access_token");
      localStorage.removeItem("bitnova_refresh_token");
      return false;
    }
  } catch {
    // Treat a malformed token as unauthenticated.
    localStorage.removeItem("bitnova_access_token");
    localStorage.removeItem("bitnova_refresh_token");
    return false;
  }

  return true;
}

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
  if (!hasAccessToken()) {
    return Promise.resolve([] as AccountBalance[]);
  }

  return apiClient<AccountBalance[]>("/accounts");
}
