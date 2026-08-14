"use client";

import { useEffect, useState } from "react";
import { getPortfolioHistory, PortfolioHistoryPoint } from "@/services/portfolio.service";

export default function PortfolioChart() {
  const [range, setRange] = useState("30D");
  const [history, setHistory] = useState<PortfolioHistoryPoint[]>([]);

  useEffect(() => {
    getPortfolioHistory(range)
      .then(setHistory)
      .catch(() => setHistory([]));
  }, [range]);

  const values = history.length
    ? history.map((item) => item.value)
    : [35, 45, 40, 65, 55, 80, 90];

  return (
    <section className="rounded-xl border border-white/10 bg-[#111318] p-6 text-white">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Portfolio Performance</h2>
        <div className="flex gap-2 text-xs text-gray-400">
          {["1D", "7D", "30D", "1Y"].map((item) => (
            <button key={item} onClick={() => setRange(item)}>
              {item}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-6 flex h-40 items-end gap-3">
        {values.map((value, index) => (
          <div
            key={index}
            className="flex-1 rounded-t bg-blue-500/70"
            style={{ height: `${Math.min(Number(value) / Math.max(...values) * 100, 100)}%` }}
          />
        ))}
      </div>

      <p className="mt-4 text-sm text-gray-400">
        Portfolio value trend based on wallet and trading activity.
      </p>
    </section>
  );
}
