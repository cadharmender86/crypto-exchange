import type {
  WalletAddressGenerateRequest,
  WalletAddressGenerateResponse,
  ReceiveAddressResponse,
} from "@/types/wallet";

export async function getReceiveAddress(
  network: string
): Promise<ReceiveAddressResponse> {
  const response = await api.get("/wallets/receive", {
    params: { network },
  });

  return response.data;
}

export async function generateReceiveAddress(
  payload: WalletAddressGenerateRequest
): Promise<WalletAddressGenerateResponse> {
  const response = await api.post(
    "/wallets/receive/generate",
    payload
  );

  return response.data;
}