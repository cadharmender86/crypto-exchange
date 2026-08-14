import { apiClient } from './apiClient';

export const getTradeHistory = async () => {
  return apiClient('/trades/history');
};

export const getTransactionHistory = async () => {
  return apiClient('/transactions/history');
};
