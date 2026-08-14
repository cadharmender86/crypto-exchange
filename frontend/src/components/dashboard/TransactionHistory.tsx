"use client";

import { useTransactionHistory } from "@/hooks/useHistory";

export default function TransactionHistory() {
  const { transactions, loading } = useTransactionHistory();

  const rows = transactions?.length ? transactions : [
    {
      type: "DEPOSIT",
      asset: "USDT",
      amount: "500 USDT",
      network: "TRC20",
      status: "COMPLETED",
      date: "Today",
    },
  ];

  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-6">
      <h2 className="mb-5 text-lg font-semibold text-white">
        Transaction History
      </h2>

      {loading ? (
        <p className="text-gray-400">Loading transactions...</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-gray-300">
            <thead className="border-b border-gray-800 text-gray-400">
              <tr>
                <th className="p-3 text-left">Type</th>
                <th className="p-3 text-left">Asset</th>
                <th className="p-3 text-left">Amount</th>
                <th className="p-3 text-left">Network</th>
                <th className="p-3 text-left">Status</th>
                <th className="p-3 text-left">Date</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((item, index) => (
                <tr key={index} className="border-b border-gray-900">
                  <td className="p-3 text-white">{item.type}</td>
                  <td className="p-3">{item.asset}</td>
                  <td className="p-3">{item.amount}</td>
                  <td className="p-3">{item.network}</td>
                  <td className="p-3 text-green-400">{item.status}</td>
                  <td className="p-3">{item.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
