"use client";

import { useEffect, useState } from "react";
import { getOrders, OrderResponse } from "@/services/order.service";

export default function OrdersPage() {
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadOrders() {
    try {
      const data = await getOrders();
      setOrders(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadOrders();

    const refresh = () => loadOrders();
    window.addEventListener("order-created", refresh);

    return () => window.removeEventListener("order-created", refresh);
  }, []);

  return (
    <main className="min-h-screen bg-[#070b14] p-6 text-white">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex justify-between">
          <h1 className="text-2xl font-bold">Orders</h1>
          <button onClick={loadOrders} className="rounded-lg bg-blue-600 px-4 py-2">
            Refresh
          </button>
        </div>

        <section className="rounded-2xl border border-white/10 bg-[#111318] p-5">
          {loading ? (
            <p className="text-gray-400">Loading orders...</p>
          ) : orders.length === 0 ? (
            <p className="text-gray-400">No orders found</p>
          ) : (
            <div className="space-y-3">
              {orders.map((order) => (
                <div key={order.id} className="flex items-center justify-between rounded-xl bg-black/20 p-4">
                  <div>
                    <p className="font-semibold">{order.symbol}</p>
                    <p className={order.side === "BUY" ? "text-green-400" : "text-red-400"}>{order.side}</p>
                  </div>
                  <div className="text-right">
                    <p>{order.amount}</p>
                    <p className="text-sm text-gray-400">{order.status}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
