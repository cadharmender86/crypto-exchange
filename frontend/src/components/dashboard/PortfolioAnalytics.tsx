"use client";

import { useWallet } from "@/hooks/useWallet";
import { useTradeHistory } from "@/hooks/useHistory";
import PortfolioChart from "./PortfolioChart";

export default function PortfolioAnalytics() {
  const { balances = [] } = useWallet() as any;
  const { trades = [] } = useTradeHistory() as any;

  const currentValue = balances.reduce(
    (sum: number, item: any) => sum + Number(item.total_balance || 0),
    0
  );

  const totalInvestment = trades.reduce(
    (sum: number, trade: any) => {
      if (trade.side === "BUY") {
        return sum + Number(trade.amount || trade.value || 0);
      }
      return sum;
    },
    0
  );

  const realizedPL = trades.reduce(
    (sum: number, trade: any) => {
      if (trade.side === "SELL") {
        return sum + Number(trade.profit_loss || 0);
      }
      return sum;
    },
    0
  );

  const unrealizedPL = currentValue - totalInvestment;

  return (
    <section className="space-y-5 rounded-xl border border-white/10 bg-[#111318] p-6 text-white">
      <div>
        <h2 className="text-lg font-semibold">Portfolio Performance</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-4">
          {[
            ["Current Value", currentValue],
            ["Total Investment", totalInvestment],
            ["Realized P/L", realizedPL],
            ["Unrealized P/L", unrealizedPL],
          ].map(([title, value]) => (
            <div key={String(title)} className="rounded-lg bg-black/20 p-4">
              <p className="text-sm text-gray-400">{title}</p>
              <p className="mt-2 text-xl font-bold">
                ₹ {Number(value).toLocaleString("en-IN", { maximumFractionDigits: 2 })}
              </p>
            </div>
          ))}
        </div>
      </div>

      <PortfolioChart />

      <div className="rounded-lg bg-black/20 p-4">
        <h3 className="font-semibold">Asset Allocation</h3>
        <div className="mt-3 space-y-2 text-sm text-gray-300">
          {balances.slice(0, 5).map((asset: any, index: number) => (
            <div key={index} className="flex justify-between">
              <span>{asset.symbol || asset.asset || `Asset ${index + 1}`}</span>
              <span>{Number(asset.total_balance || 0).toFixed(4)}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
