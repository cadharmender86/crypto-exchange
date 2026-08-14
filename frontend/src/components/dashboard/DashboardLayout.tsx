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
    <main className="min-h-screen bg-[#0b0e11] p-6 text-white">
      <div className="mx-auto max-w-7xl space-y-6">

        <DashboardHeader />

        <CryptoPortfolio
          currentValue={761000}
          netCost={700000}
          profitLoss={61000}
          tradingVolume={2500000}
        />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <EasyBuySell />
          <INRBalanceCard />
        </div>

        <CoinBalanceTable />

        <AccordionSection title="INR Deposit / Withdraw Details">
          <p className="text-gray-400">
            INR transaction history will appear here.
          </p>
        </AccordionSection>

        <AccordionSection title="Open Orders">
          <OpenOrders />
        </AccordionSection>

        <AccordionSection title="Trade History">
          <TradeHistory />
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
