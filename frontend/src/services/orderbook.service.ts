import { apiClient } from './apiClient';

export const orderBookService = {
  getOrderBook: async (symbol: string) => {
    return apiClient.get(`/orderbook/${symbol}`);
  },
};
