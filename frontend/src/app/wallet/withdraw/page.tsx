"use client";

import { useSearchParams } from "next/navigation";

export default function WithdrawPage() {
  const params = useSearchParams();
  const asset = params.get("asset") || "BTC";

  return (
    <main className="min-h-screen bg-black text-white p-8">
      <h1 className="text-3xl font-bold">Withdraw {asset}</h1>

      <div className="mt-8 max-w-xl rounded-xl border border-gray-800 p-6 space-y-5">
        <div>
          <label className="text-sm text-gray-400">Network</label>
          <select className="mt-2 w-full rounded-lg bg-gray-900 p-3">
            <option>Bitcoin Network</option>
            <option>Ethereum Network</option>
            <option>TRON Network</option>
          </select>
        </div>

        <div>
          <label className="text-sm text-gray-400">Withdrawal Address</label>
          <input className="mt-2 w-full rounded-lg bg-gray-900 p-3" placeholder="Enter wallet address" />
        </div>

        <div>
          <label className="text-sm text-gray-400">Amount</label>
          <input className="mt-2 w-full rounded-lg bg-gray-900 p-3" placeholder={`Enter ${asset} amount`} />
        </div>

        <div className="rounded-lg bg-gray-900 p-4">
          <p>Network Fee: Calculated after selection</p>
          <p className="mt-2">You Receive: Pending calculation</p>
        </div>

        <button className="w-full rounded-lg bg-blue-600 p-3">Submit Withdrawal</button>
      </div>
    </main>
  );
}
