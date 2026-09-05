import { apiFetch, getAccessToken } from "./api";

import type {
  CreatePaymentOrderRequest,
  PaymentOrderResponse,
  PaymentHistoryResponse,
} from "@/types/payment";

export async function createPaymentOrder(
  amount: number
): Promise<PaymentOrderResponse> {
  const token = getAccessToken();

  return apiFetch<PaymentOrderResponse>(
    "/payments/orders",
    {
      method: "POST",
      body: JSON.stringify({ amount }),
    },
    token ?? undefined
  );
}

export async function getPaymentHistory(): Promise<PaymentHistoryResponse> {
  const token = getAccessToken();

  return apiFetch<PaymentHistoryResponse>(
    "/payments/history",
    {},
    token ?? undefined
  );
}