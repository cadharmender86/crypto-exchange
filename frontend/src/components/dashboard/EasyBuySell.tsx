"use client";

import { useState } from "react";
import CoinSelectorModal from "./CoinSelectorModal";
import CoinIcon from "../common/CoinIcon";
import { useMarket } from "@/hooks/useMarket";

const defaultCoins = ["USDT", "BTC", "ETH", "SOL"];

export default function EasyBuySell() {
  const { assets = [] } = useMarket();
  const coins = assets.length ? assets.slice(0, 6).map((c: any) => c.symbol) : defaultCoins;

  const [selectedCoin, setSelectedCoin] = useState("USDT");
  const [mode, setMode] = useState<"BUY" | "SELL">("BUY");
  const [showCoinModal, setShowCoinModal] = useState(false);

  return (
    <section className="rounded-2xl border border-gray-800 bg-[#111318] p-6">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Easy Buy / Sell</h2>
        <button className="text-sm text-blue-400" onClick={() => setShowCoinModal(true)}>
          More Coins
        </button>
      </div>

      <div className="mb-6 flex flex-wrap gap-3">
        {coins.map((coin) => (
          <button
            key={coin}
            onClick={() => setSelectedCoin(coin)}
            className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm transition ${
              selectedCoin === coin
                ? "bg-blue-600 text-white"
                : "bg-[#1b2028] text-gray-300"
            }`}
          >
            <CoinIcon symbol={coin} size={22} />
            {coin}
          </button>
        ))}
      </div>

      <div className="mb-5 grid grid-cols-2 rounded-xl bg-[#0b0e11] p-1">
        <button
          onClick={() => setMode("BUY")}
          className={`rounded-lg py-3 font-medium ${mode === "BUY" ? "bg-green-600 text-white" : "text-gray-400"}`}
        >
          BUY
        </button>
        <button
          onClick={() => setMode("SELL")}
          className={`rounded-lg py-3 font-medium ${mode === "SELL" ? "bg-red-600 text-white" : "text-gray-400"}`}
        >
          SELL
        </button>
      </div>

      <div className="space-y-4">
        <div className="rounded-xl border border-gray-800 bg-[#0b0e11] p-4">
          <p className="text-sm text-gray-400">You Pay</p>
          <div className="mt-2 flex justify-between">
            <input
              placeholder="0.00"
              className="w-full bg-transparent text-xl text-white outline-none"
            />
            <span className="font-semibold text-white">INR</span>
          </div>
        </div>

        <div className="rounded-xl border border-gray-800 bg-[#0b0e11] p-4">
          <p className="text-sm text-gray-400">You Receive</p>
          <div className="mt-2 flex justify-between text-xl text-white">
            <span>0.00</span>
            <span>{selectedCoin}</span>
          </div>
        </div>
      </div>

      <button className="mt-5 w-full rounded-xl bg-blue-600 py-3 font-semibold text-white hover:bg-blue-700">
        Continue {mode} {selectedCoin}
      </button>

      <CoinSelectorModal
        open={showCoinModal}
        onClose={() => setShowCoinModal(false)}
        onSelect={setSelectedCoin}
      />
    </section>
  );
}
