"use client";

import { useEffect } from "react";
import { useTradeHistory } from "@/hooks/useHistory";

export default function TradeHistory() {
  const { trades, loading, refresh } = useTradeHistory() as any;

  useEffect(() => {
    const reload = () => refresh?.();
    window.addEventListener("order-created", reload);

    return () => window.removeEventListener("order-created", reload);
  }, [refresh]);

  const rows = trades?.length ? trades : [
    { pair: "BTC/INR", side: "BUY", amount: "₹2,50,000", status: "Completed" },
    { pair: "ETH/INR", side: "SELL", amount: "₹1,80,000", status: "Completed" },
    { pair: "USDT/INR", side: "BUY", amount: "₹50,000", status: "Completed" },
  ];

  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-6">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Trade History</h2>
        <button className="text-sm text-blue-400">View All</button>
      </div>

      {loading ? (
        <p className="text-gray-400">Loading trades...</p>
      ) : (
        <div className="space-y-3">
          {rows.map((trade: any, index: number) => (
            <div key={index} className="flex items-center justify-between rounded-lg bg-black/20 p-4">
              <div>
                <p className="font-semibold text-white">{trade.pair}</p>
                <p className={`text-sm font-semibold ${trade.side === "BUY" ? "text-green-400" : "text-red-400"}`}>
                  {trade.side}
                </p>
              </div>
              <div className="text-right">
                <p className="text-white">{trade.amount || trade.price}</p>
                <p className="text-xs text-gray-400">{trade.status}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
