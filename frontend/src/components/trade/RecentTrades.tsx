"use client";

const trades = [
  { price: "₹95,00,000", quantity: "0.01 BTC", time: "12:10:20" },
  { price: "₹94,98,000", quantity: "0.02 BTC", time: "12:10:15" },
];

export default function RecentTrades() {
  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-5">
      <h2 className="mb-4 text-white font-semibold">Recent Trades</h2>
      {trades.map((trade, index) => (
        <div key={index} className="flex justify-between border-b border-gray-800 py-2 text-sm">
          <span className="text-green-400">{trade.price}</span>
          <span className="text-gray-300">{trade.quantity}</span>
          <span className="text-gray-400">{trade.time}</span>
        </div>
      ))}
    </section>
  );
}
