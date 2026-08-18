"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Asset, getAssets } from "@/lib/api";

export default function MarketsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getAssets().then(setAssets).catch((err: Error) => setError(err.message));
  }, []);

  return (
    <main className="min-h-screen bg-[#070b14] px-4 py-10 text-white lg:px-8">
      <div className="mx-auto max-w-7xl">
        <Link href="/" className="text-sm text-blue-400">← BitNova</Link>
        <h1 className="mt-4 text-4xl font-bold">Markets</h1>
        <p className="mt-2 text-gray-400">Assets currently enabled by the BitNova backend.</p>

        {error && <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">{error}</div>}

        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {assets.map((asset) => (
            <div key={asset.id} className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">{asset.symbol}</h2>
                <span className="rounded-full bg-green-500/10 px-3 py-1 text-xs text-green-300">Active</span>
              </div>
              <p className="mt-2 text-sm text-gray-400">{asset.name ?? "Digital asset"}</p>
              <div className="mt-5 flex gap-2 text-xs">
                <span className="rounded-full bg-white/5 px-3 py-1 text-gray-300">Deposit {asset.deposit_enabled ? "On" : "Off"}</span>
                <span className="rounded-full bg-white/5 px-3 py-1 text-gray-300">Withdraw {asset.withdrawal_enabled ? "On" : "Off"}</span>
              </div>
            </div>
          ))}
        </div>
        {!assets.length && !error && <p className="mt-8 text-gray-500">Loading assets...</p>}
      </div>
    </main>
  );
}
