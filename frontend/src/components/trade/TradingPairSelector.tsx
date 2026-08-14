"use client";

const pairs = ["BTC/INR", "ETH/INR", "USDT/INR", "SOL/INR"];

export default function TradingPairSelector() {
  return (
    <div className="flex gap-3 overflow-x-auto rounded-xl border border-gray-800 bg-[#111318] p-4">
      {pairs.map((pair) => (
        <button key={pair} className="rounded-lg bg-gray-900 px-4 py-2 text-sm text-white hover:bg-gray-800">
          {pair}
        </button>
      ))}
    </div>
  );
}
