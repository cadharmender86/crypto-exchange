"use client";

import CoinIcon from "@/components/common/CoinIcon";
import { useWallet } from "@/hooks/useWallet";

type CoinBalance = {
  symbol: string;
  balance: string;
  netCost?: number;
  value?: number;
  change?: string;
};

type CoinBalanceTableProps = {
  showBalance?: boolean;
};

export default function CoinBalanceTable({
  showBalance = true,
}: CoinBalanceTableProps) {
  const { assets = [], loading } = useWallet();

  const coins: CoinBalance[] = assets.length
    ? assets.map((coin: any) => ({
        symbol: coin.symbol,
        balance: coin.balance || "0",
        netCost: coin.netCost || 0,
        value: coin.value || 0,
        change: coin.change || "+0.00%",
      }))
    : [
        {
          symbol: "BTC",
          balance: "0.025 BTC",
          netCost: 250000,
          value: 300000,
          change: "+2.45%",
        },
        {
          symbol: "ETH",
          balance: "2.5 ETH",
          netCost: 200000,
          value: 250000,
          change: "+1.20%",
        },
        {
          symbol: "USDT",
          balance: "500 USDT",
          netCost: 48000,
          value: 48000,
          change: "+0.05%",
        },
      ];

  return (
    <section className="rounded-xl border border-white/10 bg-[#111318] p-6">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Coin Balance</h2>

        <button className="text-sm text-blue-400">
          View All
        </button>
      </div>

      {loading && (
        <p className="mb-3 text-sm text-gray-400">
          Loading assets...
        </p>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-white/10 text-gray-400">
            <tr>
              <th className="p-3">Coin</th>
              <th className="p-3">Net Cost</th>
              <th className="p-3">Total Balance</th>
              <th className="p-3">INR Value</th>
              <th className="p-3">24h Change</th>
              <th className="p-3">Action</th>
            </tr>
          </thead>

          <tbody>
            {coins.map((coin) => (
              <tr
                key={coin.symbol}
                className="border-b border-white/10 text-white hover:bg-white/5"
              >
                <td className="p-3">
                  <div className="flex items-center gap-3">
                    <CoinIcon
                      symbol={coin.symbol}
                      size={34}
                    />

                    <span className="font-semibold">
                      {coin.symbol}
                    </span>
                  </div>
                </td>

                <td className="p-3">
                  {showBalance
                    ? `₹ ${(coin.netCost || 0).toLocaleString("en-IN")}`
                    : "₹ ••••••"}
                </td>

                <td className="p-3">
                  {showBalance
                    ? coin.balance
                    : "••••••"}
                </td>

                <td className="p-3 font-semibold">
                  {showBalance
                    ? `₹ ${(coin.value || 0).toLocaleString("en-IN")}`
                    : "₹ ••••••"}
                </td>

                <td
                  className={`p-3 ${
                    showBalance
                      ? "text-green-400"
                      : "text-slate-500"
                  }`}
                >
                  {showBalance ? coin.change : "••••"}
                </td>

                <td className="p-3">
                  <div className="flex gap-2">
                    <button className="rounded-md bg-blue-600 px-3 py-1 text-xs">
                      Deposit
                    </button>

                    <button className="rounded-md border border-white/20 px-3 py-1 text-xs">
                      Withdraw
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
