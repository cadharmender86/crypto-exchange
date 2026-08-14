"use client";

import { useWallet } from "@/hooks/useWallet";

export default function WalletSummary() {
  const { wallet, loading } = useWallet();

  if (loading) {
    return <div className="rounded-xl bg-[#11161c] p-5 text-gray-400">Loading wallet...</div>;
  }

  return (
    <section className="rounded-xl border border-gray-800 bg-[#11161c] p-5 text-white">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Wallet Overview</h2>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm">View Wallet</button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card title="Total Wallet Value" value={wallet?.totalValue ?? "₹0"} />
        <Card title="Available INR" value={wallet?.available ?? "₹0"} />
        <Card title="Locked Balance" value={wallet?.locked ?? "₹0"} />
        <Card title="Crypto Value" value={wallet?.cryptoValue ?? "₹0"} />
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <button className="rounded-lg border border-gray-700 px-5 py-2">Deposit</button>
        <button className="rounded-lg border border-gray-700 px-5 py-2">Withdraw</button>
        <button className="rounded-lg border border-gray-700 px-5 py-2">Transfer</button>
      </div>
    </section>
  );
}

function Card({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-lg bg-gray-900 p-4">
      <p className="text-sm text-gray-400">{title}</p>
      <h3 className="mt-2 text-xl font-semibold">{value}</h3>
    </div>
  );
}
