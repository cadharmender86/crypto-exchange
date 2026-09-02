import { apiFetch } from "./api";
import type {
  CreatePaymentOrderRequest,
  PaymentOrderResponse,
} from "@/types/payment";

export async function createPaymentOrder(
  payload: CreatePaymentOrderRequest
): Promise<PaymentOrderResponse> {
  return apiFetch("/api/v1/payments/orders", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}