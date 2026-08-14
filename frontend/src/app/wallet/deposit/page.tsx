"use client";

import { useSearchParams } from "next/navigation";

export default function DepositPage() {
  const params = useSearchParams();
  const asset = params.get("asset") || "BTC";

  return (
    <main className="min-h-screen bg-black text-white p-8">
      <h1 className="text-3xl font-bold">Deposit {asset}</h1>

      <div className="mt-8 max-w-xl rounded-xl border border-gray-800 p-6">
        <h2 className="text-xl font-semibold">Select Network</h2>
        <div className="mt-4 space-y-3">
          <button className="w-full rounded-lg bg-gray-900 p-3 text-left">Bitcoin Network</button>
          <button className="w-full rounded-lg bg-gray-900 p-3 text-left">Ethereum Network</button>
          <button className="w-full rounded-lg bg-gray-900 p-3 text-left">TRON Network</button>
        </div>

        <div className="mt-8 rounded-lg bg-gray-900 p-4">
          <p className="text-sm text-gray-400">Deposit Address</p>
          <p className="mt-2 break-all">Address will be generated after network selection</p>
        </div>

        <button className="mt-6 rounded-lg bg-blue-600 px-6 py-3">Generate Address</button>
      </div>
    </main>
  );
}
