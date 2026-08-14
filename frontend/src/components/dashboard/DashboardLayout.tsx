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
import OpenOrders from "./OpenOrders";
import TradeHistory from "./TradeHistory";
import TransactionHistory from "./TransactionHistory";
import WalletSummary from "../wallet/WalletSummary";
import AccordionSection from "./AccordionSection";
import DashboardHeader from "./DashboardHeader";
import PortfolioAnalytics from "./PortfolioAnalytics";

export default function DashboardLayout() {
  return (
    <main className="flex min-h-screen w-full overflow-hidden bg-[#070b10] pb-16 text-white lg:pb-0">
      <aside className="hidden lg:block">
        <Sidebar />
      </aside>

      <section className="min-w-0 flex-1 overflow-y-auto px-4 py-4 md:px-6 lg:px-8">
        <DashboardHeader />
        <AdvertisementBanner />

        <div className="mt-6 space-y-6">
          <div>
            <h1 className="text-2xl font-bold md:text-3xl">Dashboard</h1>
            <p className="text-sm text-gray-400">Manage your portfolio, wallet and trading activity</p>
          </div>

          <DashboardStats />

          <CryptoPortfolio
            currentValue={761000}
            netCost={700000}
            profitLoss={61000}
            tradingVolume={2500000}
          />

          <PortfolioAnalytics />

          <WalletSummary
            totalValue="₹7,61,000"
            available="₹50,000"
            locked="₹10,000"
          />

          <div className="grid grid-cols-1 gap-5 xl:grid-cols-12">
            <div className="xl:col-span-5"><EasyBuySell /></div>
            <div className="xl:col-span-3"><INRBalanceCard /></div>
            <div className="xl:col-span-4"><QuickOrders /></div>
          </div>

          <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
            <div className="xl:col-span-2 min-w-0"><CoinBalanceTable /></div>
            <div className="min-w-0"><TradeHistory /></div>
          </div>

          <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
            <AccordionSection title="Open Orders"><OpenOrders /></AccordionSection>
            <AccordionSection title="Transaction History"><TransactionHistory /></AccordionSection>
          </div>
        </div>
      </section>

      <MobileBottomNav />
    </main>
  );
}
