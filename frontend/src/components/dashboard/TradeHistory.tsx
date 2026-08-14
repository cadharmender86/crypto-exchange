"use client";

const trades = [
  {
    pair: "BTC/INR",
    side: "BUY",
    price: "₹95,00,000",
    quantity: "0.01 BTC",
    fee: "₹100",
    time: "10:30",
  },
  {
    pair: "ETH/INR",
    side: "SELL",
    price: "₹3,20,000",
    quantity: "1 ETH",
    fee: "₹50",
    time: "11:15",
  },
];

export default function TradeHistory() {
  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-6">
      <h2 className="mb-5 text-lg font-semibold text-white">
        Trade History
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-sm text-gray-300">
          <thead>
            <tr className="border-b border-gray-800 text-gray-400">
              <th className="p-3 text-left">Pair</th>
              <th className="p-3 text-left">Side</th>
              <th className="p-3 text-left">Price</th>
              <th className="p-3 text-left">Quantity</th>
              <th className="p-3 text-left">Fee</th>
              <th className="p-3 text-left">Time</th>
            </tr>
          </thead>

          <tbody>
            {trades.map((trade, index) => (
              <tr key={index} className="border-b border-gray-900">
                <td className="p-3 text-white">{trade.pair}</td>
                <td
                  className={`p-3 font-semibold ${
                    trade.side === "BUY"
                      ? "text-green-400"
                      : "text-red-400"
                  }`}
                >
                  {trade.side}
                </td>
                <td className="p-3">{trade.price}</td>
                <td className="p-3">{trade.quantity}</td>
                <td className="p-3">{trade.fee}</td>
                <td className="p-3">{trade.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
