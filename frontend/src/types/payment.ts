export interface CreatePaymentOrderRequest {
  amount: number;
}

export interface PaymentOrderResponse {
  id: string;
  gateway_order_id: string;
  payment_session_id: string;
  amount: string;
  currency: string;
  status: "PENDING" | "SUCCESS" | "FAILED" | "EXPIRED";
  expires_at: string;
}