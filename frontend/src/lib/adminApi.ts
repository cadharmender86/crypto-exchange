const API_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
).replace(/\/api\/v1\/?$/, "").replace(/\/$/, "");

const ACCESS_TOKEN_KEY = "bitnova_admin_access_token";
const REFRESH_TOKEN_KEY = "bitnova_admin_refresh_token";

export type AdminSession = {
  admin_id: string;
  email: string;
  full_name: string;
  permissions: string[];
  roles: string[];
};

type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

export function getAdminAccessToken() {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function clearAdminSession() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
}

async function saveTokens(response: Response): Promise<TokenResponse> {
  const data = (await response.json()) as TokenResponse & { detail?: string };
  if (!response.ok) {
    throw new Error(data.detail || "Admin authentication failed");
  }
  window.localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
  window.localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
  return data;
}

export async function adminLogin(email: string, password: string) {
  const body = new URLSearchParams({ username: email, password });
  const response = await fetch(`${API_URL}/api/v1/admin/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  return saveTokens(response);
}

export async function getAdminMe(): Promise<AdminSession> {
  const token = getAdminAccessToken();
  if (!token) throw new Error("ADMIN_UNAUTHENTICATED");

  const response = await fetch(`${API_URL}/api/v1/admin/auth/me`, {
    cache: "no-store",
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.status === 401 || response.status === 403) {
    clearAdminSession();
    throw new Error("ADMIN_UNAUTHENTICATED");
  }
  if (!response.ok) throw new Error("Unable to load admin session");
  return response.json();
}

export async function refreshAdminSession() {
  const refreshToken = typeof window === "undefined" ? null : window.localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refreshToken) throw new Error("ADMIN_UNAUTHENTICATED");

  const response = await fetch(`${API_URL}/api/v1/admin/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  return saveTokens(response);
}

export async function adminFetch(path: string, init: RequestInit = {}) {
  const token = getAdminAccessToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let response = await fetch(`${API_URL}${path}`, { ...init, headers, cache: "no-store" });
  if (response.status === 401) {
    try {
      await refreshAdminSession();
      const newToken = getAdminAccessToken();
      if (newToken) headers.set("Authorization", `Bearer ${newToken}`);
      response = await fetch(`${API_URL}${path}`, { ...init, headers, cache: "no-store" });
    } catch {
      clearAdminSession();
      throw new Error("ADMIN_UNAUTHENTICATED");
    }
  }
  return response;
}
