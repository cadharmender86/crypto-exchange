import { apiClient } from "./apiClient";

export type CreateOrderRequest = {
  symbol: string;
  side: "BUY" | "SELL";
  amount: number;
  quote_currency: "INR";
};

export type OrderResponse = {
  id: string;
  symbol: string;
  side: string;
  status: string;
  amount: string;
};

export function getOpenOrders() {
  return apiClient<OrderResponse[]>("/orders/open");
}

export function createOrder(payload: CreateOrderRequest) {
  return apiClient<OrderResponse>("/orders", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getOrders() {
  return apiClient<OrderResponse[]>("/orders");
}
