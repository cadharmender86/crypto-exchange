"use client";

import Sidebar from "../layout/Sidebar";
import AdvertisementBanner from "./AdvertisementBanner";
import CryptoPortfolio from "./CryptoPortfolio";
import EasyBuySell from "./EasyBuySell";
import INRBalanceCard from "./INRBalanceCard";
import CoinBalanceTable from "./CoinBalanceTable";
import OpenOrders from "./OpenOrders";
import TradeHistory from "./TradeHistory";
import TransactionHistory from "./TransactionHistory";
import WalletSummary from "../wallet/WalletSummary";
import AccordionSection from "./AccordionSection";
import DashboardHeader from "./DashboardHeader";

export default function DashboardLayout() {
  return (
    <main className="flex min-h-screen w-full bg-[#070b10] text-white">
      <Sidebar />

      <section className="flex-1 overflow-x-hidden p-4 md:p-6">
        <DashboardHeader />
        <AdvertisementBanner />

        <div className="mt-6 space-y-6">
          <div className="text-2xl font-bold">Dashboard</div>

          <CryptoPortfolio
            currentValue={761000}
            netCost={700000}
            profitLoss={61000}
            tradingVolume={2500000}
          />

          <WalletSummary
            totalValue="₹7,61,000"
            available="₹50,000"
            locked="₹10,000"
          />

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
            <div className="xl:col-span-2"><EasyBuySell /></div>
            <INRBalanceCard />
          </div>

          <CoinBalanceTable />

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
            <AccordionSection title="Open Orders"><OpenOrders /></AccordionSection>
            <AccordionSection title="Trade History"><TradeHistory /></AccordionSection>
          </div>

          <AccordionSection title="Transaction History"><TransactionHistory /></AccordionSection>
        </div>
      </section>
    </main>
  );
}
