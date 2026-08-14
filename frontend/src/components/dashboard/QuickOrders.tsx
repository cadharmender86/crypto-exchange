"use client";

const orders = [
  ["₿ Buy BTC / INR", "₹2,50,000", "Open"],
  ["◆ Sell ETH / INR", "₹1,80,000", "Open"],
  ["● Buy COPY / INR", "₹75,500", "Filled"],
  ["₮ Buy USDT / INR", "₹50,000", "Filled"],
];

export default function QuickOrders() {
  return (
    <section className="rounded-xl border border-white/10 bg-[#111827] p-5">
      <div className="mb-4 flex justify-between">
        <h2 className="font-semibold">Quick Orders</h2>
        <button className="text-sm text-blue-400">View All</button>
      </div>
      <div className="space-y-4">
        {orders.map(([name, amount, status]) => (
          <div key={name} className="flex items-center justify-between text-sm">
            <div>
              <p className="font-medium">{name}</p>
              <p className="text-xs text-gray-500">Exchange order</p>
            </div>
            <div className="text-right">
              <p>{amount}</p>
              <p className={status === "Filled" ? "text-green-400" : "text-blue-400"}>{status}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
