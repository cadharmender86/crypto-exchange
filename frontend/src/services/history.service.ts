import { apiClient } from "./apiClient";

export type TradeHistoryItem = Record<string, any>;
export type TransactionHistoryItem = Record<string, any>;

export function getTradeHistory(): Promise<TradeHistoryItem[]> {
  return apiClient<TradeHistoryItem[]>("/trades/history");
}

export function getTransactionHistory(limit = 100): Promise<TransactionHistoryItem[]> {
  return apiClient<TransactionHistoryItem[]>(`/transactions/history?limit=${limit}`);
}
