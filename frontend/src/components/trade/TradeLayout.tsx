"use client";

import TradingPairSelector from "./TradingPairSelector";
import TradingChart from "./TradingChart";
import OrderBook from "./OrderBook";
import BuySellPanel from "./BuySellPanel";
import RecentTrades from "./RecentTrades";
import UserOrders from "./UserOrders";

export default function TradeLayout() {
  return (
    <main className="min-h-screen w-full bg-[#0b0e11] p-4 text-white md:p-6">
      <div className="space-y-6">
        <TradingPairSelector />

        <TradingChart />

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div className="xl:col-span-2">
            <OrderBook />
          </div>
          <BuySellPanel />
        </div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <RecentTrades />
          <UserOrders />
        </div>
      </div>
    </main>
  );
}
