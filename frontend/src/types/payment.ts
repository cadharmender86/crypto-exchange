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

export interface PaymentHistoryItem {
  id: string;

  gateway_order_id: string;
  gateway_payment_id: string | null;

  amount: string;
  currency: string;

  status: "PENDING" | "SUCCESS" | "FAILED" | "CANCELLED";

  created_at: string;
  completed_at: string | null;
}

export interface PaymentHistoryResponse {
  items: PaymentHistoryItem[];
}