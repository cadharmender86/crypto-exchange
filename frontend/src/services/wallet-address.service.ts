import { apiClient } from "./apiClient";

export type Wallet = {
  id: string;
  user_id: string;
  wallet_type: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export type WalletAddress = {
  id: string;
  wallet_id: string;
  asset_id: string;
  network: string;
  address: string;
  address_type: string;
  status: string;
  created_at: string;
  updated_at: string;
};

export function getMyWallets() {
  return apiClient<Wallet[]>("/wallets");
}

export function getWalletAddresses(walletId: string) {
  return apiClient<WalletAddress[]>(`/wallets/${encodeURIComponent(walletId)}/addresses`);
}
