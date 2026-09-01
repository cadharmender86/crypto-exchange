export interface FiatDepositListItem {
  id: string;
  user_name: string;
  user_email: string;
  bank_name: string;
  utr_number: string;
  amount: string;
  currency: string;
  status: string;
  created_at: string;
}

export interface FiatDepositListResponse {
  items: FiatDepositListItem[];
  total: number;
}