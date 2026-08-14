"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { cancelOrder, getOrder, OrderResponse } from "@/services/order.service";

export default function OrderDetailsPage() {
  const params = useParams();
  const id = params.id as string;

  const [order, setOrder] = useState<OrderResponse | null>(null);
  const [loadingCancel, setLoadingCancel] = useState(false);

  async function loadOrder() {
    const data = await getOrder(id);
    setOrder(data);
  }

  async function handleCancel() {
    if (!order) return;

    setLoadingCancel(true);
    try {
      await cancelOrder(order.id);
      await loadOrder();
      window.dispatchEvent(new CustomEvent("order-created"));
    } finally {
      setLoadingCancel(false);
    }
  }

  useEffect(() => {
    loadOrder();

    const timer = setInterval(() => {
      loadOrder();
    }, 5000);

    return () => clearInterval(timer);
  }, [id]);

  if (!order) {
    return (
      <main className="min-h-screen bg-[#070b14] p-6 text-white">
        <p className="text-gray-400">Loading order details...</p>
      </main>
    );
  }

  const canCancel = order.status === "OPEN" || order.status === "PENDING";

  return (
    <main className="min-h-screen bg-[#070b14] p-6 text-white">
      <div className="mx-auto max-w-3xl rounded-2xl border border-white/10 bg-[#111318] p-6">
        <div className="flex justify-between">
          <h1 className="text-2xl font-bold">Order Details</h1>
          <Link href="/orders" className="text-blue-400">Back</Link>
        </div>

        <div className="mt-6 grid gap-4 rounded-xl bg-black/20 p-5">
          <div>Order ID: {order.id}</div>
          <div>Pair: {order.symbol}</div>
          <div>Side: {order.side}</div>
          <div>Amount: {order.amount}</div>
          <div>Status: {order.status}</div>
          <div>Filled Quantity: {order.filled_amount || "0"}</div>
          <div>Remaining Quantity: {order.remaining_amount || order.amount}</div>
          <div>Average Price: {order.average_price || "-"}</div>
          <div>Fee: {order.fee || "-"}</div>
        </div>

        <section className="mt-8 rounded-xl bg-black/20 p-5">
          <h2 className="font-semibold">Execution Timeline</h2>
          <div className="mt-4 space-y-3 text-sm text-gray-300">
            <p>✓ Order Created</p>
            <p>{["OPEN", "PENDING"].includes(order.status) ? "⏳ Waiting for execution" : "✓ Matching completed"}</p>
            <p>{order.status === "PARTIALLY_FILLED" ? "🟡 Partially Filled" : ""}</p>
            <p>{order.status === "FILLED" ? "✓ Trade Completed" : ""}</p>
            <p>{order.status === "CANCELLED" ? "✕ Cancelled" : ""}</p>
          </div>
        </section>

        {canCancel && (
          <button
            onClick={handleCancel}
            disabled={loadingCancel}
            className="mt-6 rounded-lg border border-red-500 px-5 py-2 text-red-400"
          >
            {loadingCancel ? "Cancelling..." : "Cancel Order"}
          </button>
        )}
      </div>
    </main>
  );
}
