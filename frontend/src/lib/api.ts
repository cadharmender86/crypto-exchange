const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000/api/v1"
).replace(/\/$/, "");

type ApiErrorPayload = { detail?: string };

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function parseResponse(response: Response) {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string,
): Promise<T> {
  const headers = new Headers(options.headers);

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store",
  });

  const data = await parseResponse(response);
  if (!response.ok) {
    const payload = data as ApiErrorPayload | null;
    throw new ApiError(
      response.status,
      payload?.detail ?? `API request failed with HTTP ${response.status}`,
    );
  }
  return data as T;
}

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

export type Asset = {
  id: string;
  symbol: string;
  name?: string;
  is_active: boolean;
  deposit_enabled: boolean;
  withdrawal_enabled: boolean;
};

export type Account = {
  id: string;
  asset_id: string;
  account_type: string;
  available_balance: string;
  locked_balance: string;
  total_balance: string;
  status: string;
};

export type Wallet = {
  id: string;
  user_id: string;
  wallet_type: string;
  status: string;
};

export type Deposit = {
  id: string;
  user_id: string;
  wallet_address_id: string;
  asset_id: string;
  network: string;
  blockchain_tx_hash: string;
  amount: string;
  confirmations: number;
  status: string;
  ledger_transaction_id: string | null;
};

export async function login(email: string, password: string) {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  return apiFetch<TokenResponse>("/auth/login", {
    method: "POST",
    body,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
}

export async function register(email: string, password: string) {
  return apiFetch<{ message: string; user_id: string; email: string }>(
    "/auth/register",
    { method: "POST", body: JSON.stringify({ email, password }) },
  );
}

export function changePassword(token: string, currentPassword: string, newPassword: string) {
  return apiFetch<{ message: string }>(
    "/auth/change-password",
    {
      method: "POST",
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    },
    token,
  );
}

export function getHealth() {
  return apiFetch<{ service: string; version: string; status: string }>("/health");
}

export function getAssets() {
  return apiFetch<Asset[]>("/assets");
}

export function getAccounts(token: string) {
  return apiFetch<Account[]>("/accounts", {}, token);
}

export function getWallets(token: string) {
  return apiFetch<Wallet[]>("/wallets", {}, token);
}

export function getDeposits(token: string) {
  return apiFetch<Deposit[]>("/deposits", {}, token);
}

export function saveTokens(tokens: TokenResponse) {
  localStorage.setItem("bitnova_access_token", tokens.access_token);
  localStorage.setItem("bitnova_refresh_token", tokens.refresh_token);
}

export function getAccessToken() {
  return localStorage.getItem("bitnova_access_token");
}

export function logout() {
  localStorage.removeItem("bitnova_access_token");
  localStorage.removeItem("bitnova_refresh_token");
}
