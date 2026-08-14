"use client";

const orders = [
  {
    pair: "BTC/INR",
    side: "BUY",
    type: "LIMIT",
    price: "₹95,00,000",
    amount: "0.01 BTC",
    status: "OPEN",
  },
  {
    pair: "ETH/INR",
    side: "SELL",
    type: "MARKET",
    price: "₹3,20,000",
    amount: "1 ETH",
    status: "FILLED",
  },
];

export default function OpenOrders() {
  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-6">
      <h2 className="mb-5 text-lg font-semibold text-white">
        Open Orders
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-gray-300">
          <thead className="border-b border-gray-700 text-gray-400">
            <tr>
              <th className="p-3">Pair</th>
              <th className="p-3">Side</th>
              <th className="p-3">Type</th>
              <th className="p-3">Price</th>
              <th className="p-3">Amount</th>
              <th className="p-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order, index) => (
              <tr key={index} className="border-b border-gray-800">
                <td className="p-3 text-white">{order.pair}</td>
                <td className={`p-3 ${order.side === "BUY" ? "text-green-400" : "text-red-400"}`}>
                  {order.side}
                </td>
                <td className="p-3">{order.type}</td>
                <td className="p-3">{order.price}</td>
                <td className="p-3">{order.amount}</td>
                <td className="p-3">{order.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
