export interface WalletAddressGenerateRequest {
  asset: string;
  network: string;
}

export interface WalletAddressGenerateResponse {
  asset: string;
  network: string;
  address: string;
  derivation_index: number;
  newly_generated: boolean;
}

export interface ReceiveAddressResponse {
  generated: boolean;
  network: string;
  address?: string;
  derivation_index?: number;
}