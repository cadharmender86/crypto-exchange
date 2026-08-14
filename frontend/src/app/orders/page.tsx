"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { cancelOrder, getOrders, OrderResponse } from "@/services/order.service";

function statusClass(status: string) {
  if (status === "FILLED") return "text-green-400 bg-green-400/10";
  if (status === "CANCELLED") return "text-red-400 bg-red-400/10";
  if (status === "PARTIALLY_FILLED") return "text-yellow-400 bg-yellow-400/10";
  return "text-blue-400 bg-blue-400/10";
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState<string | null>(null);

  async function loadOrders() {
    try {
      const data = await getOrders();
      setOrders(data);
    } finally {
      setLoading(false);
    }
  }

  async function handleCancel(orderId: string) {
    setActionId(orderId);
    try {
      await cancelOrder(orderId);
      await loadOrders();
      window.dispatchEvent(new CustomEvent("order-created"));
    } finally {
      setActionId(null);
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
          <button onClick={loadOrders} className="rounded-lg bg-blue-600 px-4 py-2">Refresh</button>
        </div>

        <section className="rounded-2xl border border-white/10 bg-[#111318] p-5">
          {loading ? (
            <p className="text-gray-400">Loading orders...</p>
          ) : orders.length === 0 ? (
            <p className="text-gray-400">No orders found</p>
          ) : (
            <div className="space-y-3">
              {orders.map((order) => (
                <div key={order.id} className="flex flex-wrap items-center justify-between gap-4 rounded-xl bg-black/20 p-4">
                  <Link href={`/orders/${order.id}`} className="min-w-[150px]">
                    <p className="font-semibold">{order.symbol}</p>
                    <p className={order.side === "BUY" ? "text-green-400" : "text-red-400"}>{order.side}</p>
                  </Link>

                  <div className="text-right">
                    <p>{order.amount}</p>
                    <span className={`inline-block rounded-full px-3 py-1 text-xs ${statusClass(order.status)}`}>
                      {order.status}
                    </span>
                    {(order.status === "OPEN" || order.status === "PENDING") && (
                      <button
                        onClick={() => handleCancel(order.id)}
                        disabled={actionId === order.id}
                        className="ml-3 rounded-lg border border-red-500 px-3 py-1 text-sm text-red-400"
                      >
                        {actionId === order.id ? "Cancelling..." : "Cancel"}
                      </button>
                    )}
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
