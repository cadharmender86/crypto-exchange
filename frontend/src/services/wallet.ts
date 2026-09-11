import { apiFetch, getAccessToken } from "@/lib/api";
import type {
  WalletAddressGenerateRequest,
  WalletAddressGenerateResponse,
  ReceiveAddressResponse,
} from "@/types/wallet";

export async function getReceiveAddress(
  network: string
): Promise<ReceiveAddressResponse> {
  const token = getAccessToken() ?? undefined;

  return apiFetch<ReceiveAddressResponse>(
    `/wallets/receive?network=${encodeURIComponent(network)}`,
    {},
    token
  );
}

export async function generateReceiveAddress(
  payload: WalletAddressGenerateRequest
): Promise<WalletAddressGenerateResponse> {
  const token = getAccessToken() ?? undefined;

  return apiFetch<WalletAddressGenerateResponse>(
    "/wallets/receive/generate",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    token
  );
}