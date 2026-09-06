import { apiClient } from "@/services/apiClient";

export interface WithdrawalRequest {
  asset_id: string;
  network: string;
  destination_address: string;
  amount: string;
//   idempotency_key: string;
}

export interface WithdrawalResponse {
  id: string;
  status: string;
  amount: string;
  network: string;
  destination_address: string;
  blockchain_tx_hash?: string | null;
  created_at: string;
}

export function createWithdrawal(request: WithdrawalRequest) {
  return apiClient<WithdrawalResponse>("/withdrawals", {
    method: "POST",
    headers: {
      "Idempotency-Key": crypto.randomUUID(),
    },
    body: JSON.stringify(request),
  });
}