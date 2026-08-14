"use client";

import { useState } from "react";
import CoinSelectorModal from "./CoinSelectorModal";
import CoinIcon from "../common/CoinIcon";
import { useMarket } from "@/hooks/useMarket";

const defaultCoins = ["USDT", "BTC", "ETH", "SOL"];

export default function EasyBuySell() {
  const { assets = [] } = useMarket();
  const popularCoins = assets.length ? assets.slice(0, 4).map((c: any) => c.symbol) : defaultCoins;

  const [selectedCoin, setSelectedCoin] = useState("USDT");
  const [mode, setMode] = useState<"BUY" | "SELL">("BUY");
  const [showCoinModal, setShowCoinModal] = useState(false);

  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-6">
      <h2 className="mb-5 text-lg font-semibold text-white">Easy Buy / Sell</h2>

      <div className="mb-5 flex flex-wrap gap-2">
        {popularCoins.map((coin) => (
          <button key={coin} onClick={() => setSelectedCoin(coin)} className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm ${selectedCoin === coin ? "bg-white text-black" : "bg-gray-900 text-gray-300"}`}>
            <CoinIcon symbol={coin} size={24} />
            {coin}
          </button>
        ))}

        <button onClick={() => setShowCoinModal(true)} className="rounded-lg border border-gray-700 px-4 py-2 text-blue-400">
          More Coins
        </button>
      </div>

      <div className="mb-5 flex rounded-lg bg-gray-900 p-1">
        <button onClick={() => setMode("BUY")} className={`flex-1 rounded-md py-2 ${mode === "BUY" ? "bg-green-600 text-white" : "text-gray-400"}`}>BUY</button>
        <button onClick={() => setMode("SELL")} className={`flex-1 rounded-md py-2 ${mode === "SELL" ? "bg-red-600 text-white" : "text-gray-400"}`}>SELL</button>
      </div>

      <input placeholder="Enter INR amount" className="mb-4 w-full rounded-lg border border-gray-700 bg-transparent p-3 text-white" />

      <div className="mb-4 rounded-lg bg-gray-900 p-3 text-gray-400">
        You Receive ({selectedCoin})
      </div>

      <button className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white">
        Continue {mode} {selectedCoin}
      </button>

      <CoinSelectorModal open={showCoinModal} onClose={() => setShowCoinModal(false)} onSelect={setSelectedCoin} />
    </section>
  );
}
