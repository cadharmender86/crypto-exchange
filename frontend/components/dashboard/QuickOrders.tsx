"use client";

import { useEffect, useState } from "react";
import { getOpenOrders } from "@/services/order.service";

const fallbackOrders = [
  { pair: "BTC/INR", side: "BUY", amount: "₹2,50,000", status: "Open" },
  { pair: "ETH/INR", side: "SELL", amount: "₹1,80,000", status: "Open" },
  { pair: "USDT/INR", side: "BUY", amount: "₹50,000", status: "Filled" },
];

export default function QuickOrders() {
  const [orders, setOrders] = useState<any[]>(fallbackOrders);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadOrders() {
      try {
        setLoading(true);
        const response: any = await getOpenOrders();
        if (Array.isArray(response) && response.length) {
          setOrders(response);
        }
      } catch {
        setOrders(fallbackOrders);
      } finally {
        setLoading(false);
      }
    }

    loadOrders();
  }, []);

  return (
    <section className="rounded-2xl border border-white/10 bg-[#111318] p-5 text-white">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="font-semibold">Quick Orders</h2>
        <button className="text-sm text-blue-400">View All</button>
      </div>

      {loading ? (
        <p className="text-sm text-gray-400">Loading orders...</p>
      ) : (
        <div className="space-y-4">
          {orders.map((order, index) => (
            <div key={order.id || index} className="rounded-xl bg-black/20 p-3">
              <div className="flex justify-between">
                <div>
                  <p className="font-medium">{order.pair || order.symbol}</p>
                  <span className={order.side === "BUY" ? "text-green-400 text-xs" : "text-red-400 text-xs"}>
                    {order.side}
                  </span>
                </div>

                <div className="text-right">
                  <p className="text-sm">{order.amount || order.total_amount}</p>
                  <span className="text-blue-400 text-xs">
                    {order.status || "OPEN"}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
