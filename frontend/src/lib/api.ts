const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

export async function getHealth() {
  const response = await fetch(
    `${API_URL}/api/v1/health`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("API request failed");
  }

  return response.json();
}


export async function getAssets() {
  const response = await fetch(
    `${API_URL}/api/v1/assets`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to load assets");
  }

  return response.json();
}