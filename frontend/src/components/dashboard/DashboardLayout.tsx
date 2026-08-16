"use client";

import Sidebar from "../layout/Sidebar";
import MobileBottomNav from "../layout/MobileBottomNav";
import AdvertisementBanner from "./AdvertisementBanner";
import DashboardStats from "./DashboardStats";
import CryptoPortfolio from "./CryptoPortfolio";
import EasyBuySell from "./EasyBuySell";
import INRBalanceCard from "./INRBalanceCard";
import QuickOrders from "./QuickOrders";
import CoinBalanceTable from "./CoinBalanceTable";
import TradeHistory from "./TradeHistory";
import DashboardHeader from "./DashboardHeader";

function FuturesBanner() {
  return (
    <section className="relative min-h-[88px] overflow-hidden rounded-xl border border-blue-500/25 bg-gradient-to-r from-[#071632] via-[#09255b] to-[#07132b] px-7 py-4 shadow-[0_12px_45px_rgba(0,91,255,.12)]">
      <div className="pointer-events-none absolute -right-12 -top-20 h-48 w-48 rounded-full bg-blue-500/20 blur-3xl" />
      <div className="relative flex h-full flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-base font-bold text-white md:text-lg">2X Your Crypto Potential with Futures Trading</h2>
          <p className="mt-1 text-xs text-slate-300 md:text-sm">High liquidity. Low fees. Advanced tools.</p>
        </div>
        <button className="w-fit rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 px-6 py-2.5 text-sm font-bold text-white shadow-lg shadow-blue-600/20 transition hover:scale-[1.02]">Trade Futures Now <span className="ml-2">→</span></button>
      </div>
    </section>
  );
}

export default function DashboardLayout() {
  return (
    <main className="min-h-screen w-full overflow-x-hidden bg-[#080d12] text-white pb-16 lg:pb-0">
      <aside className="fixed inset-y-0 left-0 z-40 hidden lg:block">
        <Sidebar />
      </aside>

      <section className="min-w-0 lg:ml-[180px]">
        <DashboardHeader />

        <div className="mx-auto w-full max-w-[1162px] px-4 py-4 md:px-5 lg:px-[18px] lg:py-4">
          <AdvertisementBanner />

          <div className="mt-6">
            <div className="mb-5 flex items-end justify-between gap-4">
              <div>
                <h1 className="text-2xl font-bold tracking-tight md:text-[25px]">Dashboard</h1>
                <p className="mt-1 text-xs font-medium text-slate-300">Welcome back, Dharmender 👋</p>
              </div>
              <button className="hidden items-center gap-2 text-xs font-semibold text-white md:flex"><span className="text-slate-300">◉</span> Hide Balance</button>
            </div>

            <DashboardStats />

            <div className="mt-4">
              <CryptoPortfolio currentValue={761000} netCost={700000} profitLoss={61000} tradingVolume={2500000} />
            </div>

            <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-[37fr_30fr_33fr]">
              <EasyBuySell />
              <INRBalanceCard />
              <QuickOrders />
            </div>

            <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-[67fr_33fr]">
              <CoinBalanceTable />
              <TradeHistory />
            </div>

            <div className="mt-4"><FuturesBanner /></div>
          </div>
        </div>
      </section>

      <MobileBottomNav />
    </main>
  );
}
