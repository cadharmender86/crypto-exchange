export const CUSTOMER_APP_URL = (
  process.env.NEXT_PUBLIC_CUSTOMER_APP_URL ?? "http://localhost:3000"
).replace(/\/$/, "");

export function customerUrl(path = "") {
  return `${CUSTOMER_APP_URL}${path}`;
}
