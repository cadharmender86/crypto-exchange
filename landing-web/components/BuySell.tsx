"use client";

import { useState } from "react";
import { customerUrl } from "@/lib/site";

export default function BuySell() {
  const [mode, setMode] = useState<"buy" | "sell">("buy");

  return (
    <section className="bg-[#0a0f1b] py-24">
      <div className="mx-auto max-w-7xl px-4 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-2">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">Easy trading</p>
            <h2 className="mt-4 text-4xl font-bold text-white">Buy and sell crypto in seconds</h2>
            <p className="mt-5 max-w-lg leading-7 text-gray-400">Get a simple trading experience with transparent pricing, secure wallets and fast order execution.</p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <div className="mb-6 grid grid-cols-2 rounded-xl bg-black/30 p-1">
              <button onClick={() => setMode("buy")} className={`rounded-lg py-3 font-semibold ${mode === "buy" ? "bg-blue-500 text-white" : "text-gray-400"}`}>Buy</button>
              <button onClick={() => setMode("sell")} className={`rounded-lg py-3 font-semibold ${mode === "sell" ? "bg-blue-500 text-white" : "text-gray-400"}`}>Sell</button>
            </div>
            <div className="rounded-xl border border-white/10 bg-black/20 p-4 text-gray-400">INR → USDT trading preview</div>
            <a href={customerUrl("/buy-sell")} className="mt-6 block w-full rounded-xl bg-blue-500 py-4 text-center font-semibold text-white hover:bg-blue-600">{mode === "buy" ? "Buy USDT" : "Sell USDT"}</a>
          </div>
        </div>
      </div>
    </section>
  );
}
