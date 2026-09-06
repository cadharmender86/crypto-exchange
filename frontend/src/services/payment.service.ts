import { apiClient } from "./apiClient";

export interface CreateINRDepositRequest {
  amount: number;
}

export interface CreateINRDepositResponse {
  order_id: string;
  payment_session_id: string;
  amount: string;
  currency: string;
}

export function createINRDeposit(amount: number) {
  return apiClient<CreateINRDepositResponse>(
    "/payments/cashfree/create-order",
    {
      method: "POST",
      body: JSON.stringify({ amount }),
    }
  );
}