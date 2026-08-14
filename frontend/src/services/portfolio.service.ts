import { apiClient } from "@/lib/apiClient";

export interface PortfolioHistoryPoint {
  date: string;
  value: number;
}

export async function getPortfolioHistory(
  range: string = "30D"
): Promise<PortfolioHistoryPoint[]> {
  return apiClient<PortfolioHistoryPoint[]>(
    `/portfolio/history?range=${range}`
  );
}
