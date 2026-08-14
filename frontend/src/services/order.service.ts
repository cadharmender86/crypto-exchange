import { apiClient } from "./apiClient";

export function getOpenOrders() {
  return apiClient("/orders/open");
}

export function createOrder(payload: unknown) {
  return apiClient("/orders", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
