"use client";

import { useState } from "react";

const popularCoins = ["USDT", "BTC", "ETH", "SOL"];
const moreCoins = ["XRP", "ADA", "DOGE", "DOT", "MATIC", "LTC", "AVAX", "BNB"];

export default function EasyBuySell() {
  const [selectedCoin, setSelectedCoin] = useState("USDT");
  const [mode, setMode] = useState<"BUY" | "SELL">("BUY");
  const [showMoreCoins, setShowMoreCoins] = useState(false);

  const coins = showMoreCoins
    ? [...popularCoins, ...moreCoins]
    : popularCoins;

  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-6">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">
          Easy Buy / Sell
        </h2>
      </div>

      <div className="mb-5 flex flex-wrap gap-2">
        {coins.map((coin) => (
          <button
            key={coin}
            onClick={() => setSelectedCoin(coin)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              selectedCoin === coin
                ? "bg-white text-black"
                : "bg-gray-900 text-gray-300"
            }`}
          >
            {coin}
          </button>
        ))}

        <button
          onClick={() => setShowMoreCoins(!showMoreCoins)}
          className="rounded-lg border border-gray-700 px-4 py-2 text-sm text-blue-400"
        >
          {showMoreCoins ? "Less" : "More Coins"}
        </button>
      </div>

      <div className="mb-5 flex rounded-lg bg-gray-900 p-1">
        <button
          onClick={() => setMode("BUY")}
          className={`flex-1 rounded-md py-2 ${
            mode === "BUY"
              ? "bg-green-600 text-white"
              : "text-gray-400"
          }`}
        >
          BUY
        </button>

        <button
          onClick={() => setMode("SELL")}
          className={`flex-1 rounded-md py-2 ${
            mode === "SELL"
              ? "bg-red-600 text-white"
              : "text-gray-400"
          }`}
        >
          SELL
        </button>
      </div>

      <div className="space-y-4">
        <div>
          <label className="text-sm text-gray-400">
            You Pay (INR)
          </label>
          <input
            placeholder="Enter amount"
            className="mt-2 w-full rounded-lg border border-gray-700 bg-transparent p-3 text-white"
          />
        </div>

        <div>
          <label className="text-sm text-gray-400">
            You Receive ({selectedCoin})
          </label>
          <input
            placeholder="Estimated amount"
            disabled
            className="mt-2 w-full rounded-lg border border-gray-700 bg-gray-900 p-3 text-gray-400"
          />
        </div>

        <button className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white">
          Continue {mode} {selectedCoin}
        </button>
      </div>
    </section>
  );
}
