"use client";

import DashboardHeader from "./DashboardHeader";
import CryptoPortfolio from "./CryptoPortfolio";
import EasyBuySell from "./EasyBuySell";
import INRBalanceCard from "./INRBalanceCard";
import CoinBalanceTable from "./CoinBalanceTable";
import AccordionSection from "./AccordionSection";
import OpenOrders from "./OpenOrders";
import TradeHistory from "./TradeHistory";

export default function DashboardLayout() {
  return (
    <main className="min-h-screen w-full bg-[#0b0e11] text-white">
      <div className="w-full space-y-6 p-4 md:p-6">

        <DashboardHeader />

        <CryptoPortfolio
          currentValue={761000}
          netCost={700000}
          profitLoss={61000}
          tradingVolume={2500000}
        />

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div className="xl:col-span-2">
            <EasyBuySell />
          </div>

          <div>
            <INRBalanceCard />
          </div>
        </div>

        <CoinBalanceTable />

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <AccordionSection title="Open Orders">
            <OpenOrders />
          </AccordionSection>

          <AccordionSection title="Trade History">
            <TradeHistory />
          </AccordionSection>
        </div>

        <AccordionSection title="INR Deposit / Withdraw Details">
          <p className="text-gray-400">
            INR transaction history will appear here.
          </p>
        </AccordionSection>

        <AccordionSection title="Crypto Deposit / Withdraw Details">
          <p className="text-gray-400">
            Crypto deposit and withdrawal history will appear here.
          </p>
        </AccordionSection>

      </div>
    </main>
  );
}
