"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { getOrders, OrderResponse } from "@/services/order.service";

export default function OrderDetailsPage() {
  const params = useParams();
  const id = params.id as string;

  const [order, setOrder] = useState<OrderResponse | null>(null);

  useEffect(() => {
    async function load() {
      const orders = await getOrders();
      const found = orders.find((item) => item.id === id);
      setOrder(found || null);
    }

    load();
  }, [id]);

  if (!order) {
    return (
      <main className="min-h-screen bg-[#070b14] p-6 text-white">
        <p className="text-gray-400">Loading order details...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#070b14] p-6 text-white">
      <div className="mx-auto max-w-3xl rounded-2xl border border-white/10 bg-[#111318] p-6">
        <div className="flex justify-between">
          <h1 className="text-2xl font-bold">Order Details</h1>
          <Link href="/orders" className="text-blue-400">Back</Link>
        </div>

        <div className="mt-6 space-y-4">
          <div><span className="text-gray-400">Order ID:</span> {order.id}</div>
          <div><span className="text-gray-400">Pair:</span> {order.symbol}</div>
          <div><span className="text-gray-400">Side:</span> {order.side}</div>
          <div><span className="text-gray-400">Amount:</span> {order.amount}</div>
          <div><span className="text-gray-400">Status:</span> {order.status}</div>
        </div>
      </div>
    </main>
  );
}
