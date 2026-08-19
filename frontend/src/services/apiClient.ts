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

  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (typeof window !== "undefined") {
    const token = localStorage.getItem("bitnova_access_token");

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
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
      // Keep the HTTP status message when the response is not JSON.
    }

    throw new Error(message);
  }

  return response.json();
}
