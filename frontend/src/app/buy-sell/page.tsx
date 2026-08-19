"use client";

import Link from "next/link";
import DashboardHeader from "@/components/dashboard/DashboardHeader";
import BuySell from "@/components/BuySell";

export default function BuySellPage() {
  return (
    <main className="min-h-screen bg-[#080d12] text-white">
      <DashboardHeader />
      <div className="mx-auto flex max-w-[1400px] items-center justify-between px-3 pt-4 md:px-5">
        <div>
          <Link href="/dashboard" className="text-xs font-semibold text-slate-400 hover:text-white">← Dashboard</Link>
          <h1 className="mt-2 text-xl font-bold">Spot Trading</h1>
          <p className="mt-1 text-xs text-slate-500">Trade crypto against INR with live market prices.</p>
        </div>
      </div>
      <BuySell />
    </main>
  );
}
