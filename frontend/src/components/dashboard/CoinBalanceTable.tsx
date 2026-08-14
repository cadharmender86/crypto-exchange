"use client";

import CoinIcon from "@/components/common/CoinIcon";
import { useWallet } from "@/hooks/useWallet";

type CoinBalance = {
  symbol: string;
  balance: string;
  netCost?: number;
  value?: number;
};

export default function CoinBalanceTable() {
  const { assets = [], loading } = useWallet();

  const coins: CoinBalance[] = assets.length
    ? assets
    : [
        { symbol: "BTC", balance: "0.025 BTC", netCost: 250000, value: 300000 },
        { symbol: "ETH", balance: "2.5 ETH", netCost: 200000, value: 250000 },
        { symbol: "USDT", balance: "500 USDT", netCost: 48000, value: 48000 },
      ];

  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-6">
      <h2 className="mb-5 text-lg font-semibold text-white">Coin Balance</h2>

      {loading && <p className="mb-3 text-sm text-gray-400">Loading assets...</p>}

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-gray-800 text-gray-400">
            <tr>
              <th className="p-3">Coin</th>
              <th className="p-3">Net Cost</th>
              <th className="p-3">Balance</th>
              <th className="p-3">INR Value</th>
              <th className="p-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {coins.map((coin) => (
              <tr key={coin.symbol} className="border-b border-gray-800 text-white">
                <td className="p-3">
                  <div className="flex items-center gap-3">
                    <CoinIcon symbol={coin.symbol} size={34} />
                    <span className="font-semibold">{coin.symbol}</span>
                  </div>
                </td>
                <td className="p-3">₹ {(coin.netCost || 0).toLocaleString("en-IN")}</td>
                <td className="p-3">{coin.balance}</td>
                <td className="p-3">₹ {(coin.value || 0).toLocaleString("en-IN")}</td>
                <td className="p-3">
                  <button className="mr-2 rounded-md bg-blue-600 px-3 py-1 text-xs">Deposit</button>
                  <button className="rounded-md bg-gray-700 px-3 py-1 text-xs">Withdraw</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
