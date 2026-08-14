import { apiFetch } from "@/lib/api";

export interface PortfolioHistoryPoint {
  date: string;
  value: number;
}

export async function getPortfolioHistory(
  range: string = "30D"
): Promise<PortfolioHistoryPoint[]> {
  return apiFetch<PortfolioHistoryPoint[]>(
    `/portfolio/history?range=${range}`
  );
}