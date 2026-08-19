import { apiClient } from "./apiClient";

function hasAccessToken() {
  return typeof window !== "undefined" && Boolean(localStorage.getItem("bitnova_access_token"));
}

export type CreateOrderRequest = {
  base_asset_id: string;
  quote_asset_id: string;
  side: "BUY" | "SELL";
  order_type?: "LIMIT";
  price: number;
  quantity: number;
  client_order_id?: string;
};

export type OrderFill = {
  id: string;
  price: string;
  quantity: string;
  created_at?: string;
};

export type OrderResponse = {
  id: string;
  symbol: string;
  side: string;
  status: string;
  amount: string;
  filled_amount?: string;
  remaining_amount?: string;
  average_price?: string;
  fee?: string;
  created_at?: string;
};

export function getOpenOrders() {
  if (!hasAccessToken()) {
    return Promise.resolve([] as OrderResponse[]);
  }

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

export function getOrder(orderId: string) {
  return apiClient<OrderResponse>(`/orders/${orderId}`);
}

export function getOrderFills(orderId: string) {
  return apiClient<OrderFill[]>(`/orders/${orderId}/fills`);
}

export function cancelOrder(orderId: string) {
  return apiClient<OrderResponse>(`/orders/${orderId}/cancel`, {
    method: "POST",
  });
}
