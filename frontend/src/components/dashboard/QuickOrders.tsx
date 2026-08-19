"use client";

import { useEffect, useState } from "react";
import { getOpenOrders } from "@/services/order.service";

const fallbackOrders = [
  { pair: "BTC/INR", side: "BUY", amount: "₹2,50,000", status: "Open", note: "Add funds to your account" },
  { pair: "ETH/INR", side: "SELL", amount: "₹1,80,000", status: "Open", note: "Sell ETH funds to bank" },
  { pair: "USDT/INR", side: "BUY", amount: "₹50,000", status: "Filled", note: "Transfer to another wallet" },
  { pair: "SOL/INR", side: "BUY", amount: "₹30,000", status: "Filled", note: "Completed order" },
];

type QuickOrdersProps = {
  showBalance?: boolean;
};

export default function QuickOrders({
  showBalance = true,
}: QuickOrdersProps) {
  const [orders, setOrders] = useState<any[]>(fallbackOrders);
  async function loadOrders() { try { const data: any = await getOpenOrders(); if (Array.isArray(data) && data.length) setOrders(data); } catch { setOrders(fallbackOrders); } }
  useEffect(() => { loadOrders(); const refresh = () => loadOrders(); window.addEventListener("order-created", refresh); return () => window.removeEventListener("order-created", refresh); }, []);

  return (
    <section className="h-full rounded-lg border border-white/[0.06] bg-[#10161d] p-4 text-white">
      <div className="mb-3 flex items-center justify-between"><h2 className="text-sm font-bold">Quick Orders</h2><button className="text-xs font-semibold text-blue-400">View All</button></div>
      <div className="divide-y divide-white/[0.06]">
        {orders.slice(0, 4).map((order, index) => <div key={index} className="flex items-center gap-2 py-2.5 first:pt-1"><span className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${order.side === "BUY" ? "bg-emerald-500/15 text-emerald-300" : "bg-red-500/15 text-red-300"} text-xs font-bold`}>{(order.pair || order.symbol || "?")[0]}</span><div className="min-w-0 flex-1"><p className={`text-[10px] font-bold ${order.side === "BUY" ? "text-emerald-400" : "text-red-400"}`}>{order.side} {order.pair || order.symbol}</p><p className="truncate text-[8px] text-slate-500">{order.note || "Order details"}</p></div><div className="text-right"><p className="text-[10px] font-semibold">{showBalance ? order.amount : "••••••"}</p><p className={`text-[9px] font-bold ${order.status === "Filled" ? "text-emerald-400" : "text-emerald-400"}`}>{order.status}</p></div></div>)}
      </div>
    </section>
  );
}
