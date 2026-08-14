import apiClient from './apiClient';

export const getTradeHistory = async () => {
  const response = await apiClient.get('/trades/history');
  return response.data;
};

export const getTransactionHistory = async () => {
  const response = await apiClient.get('/transactions/history');
  return response.data;
};
