"use client";

import { useMarket } from "@/hooks/useMarket";

export default function MarketTicker() {
  const { ticker, loading } = useMarket();

  const markets = ticker ?? [];

  if (loading) {
    return <div className="rounded-xl border border-white/10 bg-[#111820] px-4 py-3 text-gray-400">Loading markets...</div>;
  }

  return (
    <div className="w-full overflow-x-auto rounded-xl border border-white/10 bg-[#111820] px-4 py-3">
      <div className="flex min-w-max gap-8">
        {markets.map((market: any) => (
          <div key={market.pair} className="flex items-center gap-3 text-sm">
            <span className="font-semibold text-white">{market.pair}</span>
            <span className="text-gray-300">{market.price}</span>
            <span className="text-green-400">{market.change}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
