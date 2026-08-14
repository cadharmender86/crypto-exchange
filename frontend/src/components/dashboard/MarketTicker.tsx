"use client";

const markets = [
  { pair: "BTC/INR", price: "₹95,20,000", change: "+2.4%" },
  { pair: "ETH/INR", price: "₹3,25,000", change: "+1.8%" },
  { pair: "USDT/INR", price: "₹96.40", change: "+0.2%" },
  { pair: "SOL/INR", price: "₹14,500", change: "+3.1%" },
];

export default function MarketTicker() {
  return (
    <div className="w-full overflow-x-auto rounded-xl border border-white/10 bg-[#111820] px-4 py-3">
      <div className="flex min-w-max gap-8">
        {markets.map((market) => (
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
