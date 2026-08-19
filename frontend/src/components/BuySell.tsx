"use client";

import { useState } from "react";

export default function BuySell() {
  const [mode, setMode] = useState<"buy" | "sell">("buy");
  const [payAmount, setPayAmount] = useState("");
  const [receiveAmount, setReceiveAmount] = useState("");

  const payCurrency = mode === "buy" ? "INR" : "USDT";
  const receiveCurrency = mode === "buy" ? "USDT" : "INR";

  const handleModeChange = (newMode: "buy" | "sell") => {
    setMode(newMode);
    setPayAmount("");
    setReceiveAmount("");
  };

  return (
    <section className="bg-[#0a0f1b] py-24">
      <div className="mx-auto max-w-7xl px-4 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-2">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
              Easy trading
            </p>

            <h2 className="mt-4 text-4xl font-bold text-white">
              Buy and sell crypto in seconds
            </h2>

            <p className="mt-5 max-w-lg leading-7 text-gray-400">
              Get a simple trading experience with transparent pricing,
              secure wallets and fast order execution.
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <div className="mb-6 grid grid-cols-2 rounded-xl bg-black/30 p-1">
              <button
                type="button"
                onClick={() => handleModeChange("buy")}
                className={`rounded-lg py-3 font-semibold ${
                  mode === "buy"
                    ? "bg-emerald-500 text-white hover:bg-emerald-600"
                    : "text-gray-400"
                }`}
              >
                Buy
              </button>

              <button
                type="button"
                onClick={() => handleModeChange("sell")}
                className={`rounded-lg py-3 font-semibold ${
                  mode === "sell"
                    ? "bg-red-500 text-white hover:bg-red-600"
                    : "text-gray-400"
                }`}
              >
                Sell
              </button>
            </div>

            <label className="text-sm text-gray-400">
              You pay
            </label>

            <div className="mt-2 flex items-center justify-between rounded-xl border border-white/10 bg-black/20 p-4">
              <input
                type="number"
                min="0"
                step="any"
                value={payAmount}
                onChange={(e) => setPayAmount(e.target.value)}
                placeholder="0.00"
                className="w-full bg-transparent text-xl text-white outline-none"
              />

              <span className="font-semibold text-white">
                {payCurrency}
              </span>
            </div>

            <div className="my-5 text-center text-gray-500">
              ↓
            </div>

            <label className="text-sm text-gray-400">
              You receive
            </label>

            <div className="mt-2 flex items-center justify-between rounded-xl border border-white/10 bg-black/20 p-4">
              <input
                type="number"
                min="0"
                step="any"
                value={receiveAmount}
                onChange={(e) => setReceiveAmount(e.target.value)}
                placeholder="0.00"
                className="w-full bg-transparent text-xl text-white outline-none"
              />

              <span className="font-semibold text-white">
                {receiveCurrency}
              </span>
            </div>

            <button
              type="button"
              className={`mt-6 w-full rounded-xl py-4 font-semibold text-white ${mode === "buy" ? "bg-emerald-500 hover:bg-emerald-600" : "bg-red-500 hover:bg-red-600"}`}
            >
              {mode === "buy" ? "Buy USDT" : "Sell USDT"}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
