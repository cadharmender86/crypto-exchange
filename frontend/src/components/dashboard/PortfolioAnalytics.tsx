"use client";

import { useWallet } from "@/hooks/useWallet";

export default function PortfolioAnalytics() {
  const { balances = [] } = useWallet() as any;

  const totalValue = balances.reduce(
    (sum: number, item: any) => sum + Number(item.total_balance || 0),
    0
  );

  return (
    <section className="rounded-xl border border-white/10 bg-[#111318] p-6 text-white">
      <h2 className="text-lg font-semibold">Portfolio Performance</h2>

      <div className="mt-5 grid gap-4 md:grid-cols-4">
        <div className="rounded-lg bg-black/20 p-4">
          <p className="text-sm text-gray-400">Current Value</p>
          <p className="mt-2 text-xl font-bold">₹ {totalValue.toFixed(2)}</p>
        </div>

        <div className="rounded-lg bg-black/20 p-4">
          <p className="text-sm text-gray-400">Total Investment</p>
          <p className="mt-2 text-xl font-bold">₹ 0.00</p>
        </div>

        <div className="rounded-lg bg-black/20 p-4">
          <p className="text-sm text-gray-400">Realized P/L</p>
          <p className="mt-2 text-xl font-bold text-green-400">₹ 0.00</p>
        </div>

        <div className="rounded-lg bg-black/20 p-4">
          <p className="text-sm text-gray-400">Unrealized P/L</p>
          <p className="mt-2 text-xl font-bold">₹ 0.00</p>
        </div>
      </div>
    </section>
  );
}
