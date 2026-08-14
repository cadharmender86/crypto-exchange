import { apiClient } from './apiClient';

export const tradeService = {
  getRecentTrades: async (symbol: string) => {
    return apiClient.get(`/trades/recent/${symbol}`);
  },
};
