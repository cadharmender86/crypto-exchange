"use client";

import { useTransactionHistory } from "@/hooks/useHistory";

export default function TransactionHistory() {
  const { transactions, loading } = useTransactionHistory();

  const rows = transactions?.length
    ? transactions
    : [
        {
          type: "DEPOSIT",
          asset: "USDT",
          amount: "500 USDT",
          network: "TRC20",
          status: "COMPLETED",
          date: "Today",
        },
        {
          type: "WITHDRAW",
          asset: "BTC",
          amount: "0.005 BTC",
          network: "BTC Network",
          status: "COMPLETED",
          date: "Yesterday",
        },
        {
          type: "DEPOSIT",
          asset: "INR",
          amount: "₹50,000",
          network: "Bank Transfer",
          status: "COMPLETED",
          date: "12 Aug",
        },
      ];

  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-6">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Transaction History</h2>
        <button className="text-sm text-blue-400">View All</button>
      </div>

      {loading ? (
        <p className="text-gray-400">Loading transactions...</p>
      ) : (
        <div className="space-y-3">
          {rows.map((item, index) => (
            <div
              key={index}
              className="flex flex-wrap items-center justify-between rounded-lg bg-black/20 p-4"
            >
              <div>
                <p className="font-semibold text-white">
                  {item.type} {item.asset}
                </p>
                <p className="text-sm text-gray-400">
                  {item.network} • {item.date}
                </p>
              </div>

              <div className="text-right">
                <p
                  className={`font-semibold ${
                    item.type === "WITHDRAW"
                      ? "text-red-400"
                      : "text-green-400"
                  }`}
                >
                  {item.amount}
                </p>
                <p className="text-xs text-gray-400">{item.status}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
