import { getAccessToken } from "@/lib/auth";

const configuredBaseUrl =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const API_BASE_URL = configuredBaseUrl.replace(/\/$/, "").endsWith("/api/v1")
  ? configuredBaseUrl.replace(/\/$/, "")
  : `${configuredBaseUrl.replace(/\/$/, "")}/api/v1`;

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);

  // Default Content-Type
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  // Automatically attach JWT token
  const token = getAccessToken();

  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    let message = `API Error: ${response.status}`;

    try {
      const data = await response.json();

      if (typeof data?.detail === "string") {
        message = data.detail;
      }
    } catch {
      // Keep HTTP status if response isn't JSON.
    }

    throw new Error(message);
  }

  return response.json();
}