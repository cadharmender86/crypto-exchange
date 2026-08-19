"use client";

import { useEffect, useMemo, useState } from "react";
import CoinIcon from "@/components/common/CoinIcon";
import { getTransactionHistory, type TransactionHistoryItem } from "@/services/history.service";

const PAGE_SIZE = 20;

type Filter = "ALL" | "DEPOSIT" | "WITHDRAWAL" | "TRADE" | "TRANSFER";

function formatAmount(value: string | number, asset: string, direction: string) {
  const amount = Number(value);
  const sign = direction === "CREDIT" ? "+" : "-";
  return `${sign}${Math.abs(amount).toLocaleString("en-IN", { maximumFractionDigits: 8 })} ${asset}`;
}

function formatDate(value: string) {
  return new Date(value).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function normalizeType(value: unknown): string {
  return String(value ?? "").toUpperCase();
}

export default function HistoryPage() {
  const [items, setItems] = useState<TransactionHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<Filter>("ALL");
  const [asset, setAsset] = useState("ALL");
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);

  useEffect(() => {
    let active = true;

    getTransactionHistory(100)
      .then((data) => {
        if (active) setItems(data);
      })
      .catch(() => {
        if (active) setError("Unable to load transaction history. Please try again.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const assets = useMemo(() => {
    return Array.from(new Set(items.map((item) => String(item.asset ?? "").toUpperCase()).filter(Boolean))).sort();
  }, [items]);

  const filtered = useMemo(() => {
    const text = query.trim().toLowerCase();

    return items.filter((item) => {
      const type = normalizeType(item.type);
      const itemAsset = normalizeType(item.asset);
      const reference = String(item.reference ?? "").toLowerCase();
      const description = String(item.description ?? "").toLowerCase();

      const typeMatch = filter === "ALL" || type === filter;
      const assetMatch = asset === "ALL" || itemAsset === asset;
      const queryMatch = !text || reference.includes(text) || description.includes(text) || itemAsset.toLowerCase().includes(text) || type.toLowerCase().includes(text);

      return typeMatch && assetMatch && queryMatch;
    });
  }, [items, filter, asset, query]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const visible = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  function changeFilter(next: Filter) {
    setFilter(next);
    setPage(1);
  }

  function changeAsset(next: string) {
    setAsset(next);
    setPage(1);
  }

  function changeQuery(next: string) {
    setQuery(next);
    setPage(1);
  }

  return (
    <main className="min-h-screen bg-[#080d12] px-4 py-6 text-white md:px-6 lg:px-8">
      <div className="mx-auto max-w-[1440px]">
        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight">Transaction History</h1>
          <p className="mt-1 text-sm text-slate-400">View your deposits, withdrawals, trades and transfers.</p>
        </div>

        <section className="overflow-hidden rounded-xl border border-white/10 bg-[#0d141c]">
          <div className="flex flex-col gap-4 border-b border-white/10 p-5 xl:flex-row xl:items-center xl:justify-between">
            <div className="flex flex-wrap gap-1 rounded-lg border border-white/10 bg-[#080d12] p-1">
              {(["ALL", "DEPOSIT", "WITHDRAWAL", "TRADE", "TRANSFER"] as Filter[]).map((item) => (
                <button key={item} onClick={() => changeFilter(item)} className={`rounded-md px-3 py-2 text-xs font-medium transition ${filter === item ? "bg-blue-600 text-white" : "text-slate-400 hover:text-white"}`}>
                  {item === "ALL" ? "All" : item.charAt(0) + item.slice(1).toLowerCase()}
                </button>
              ))}
            </div>

            <div className="flex flex-col gap-2 sm:flex-row">
              <input value={query} onChange={(event) => changeQuery(event.target.value)} placeholder="Search reference, asset..." className="w-full rounded-lg border border-white/10 bg-[#080d12] px-4 py-2.5 text-sm outline-none placeholder:text-slate-600 focus:border-blue-500 sm:w-64" />
              <select value={asset} onChange={(event) => changeAsset(event.target.value)} className="rounded-lg border border-white/10 bg-[#080d12] px-4 py-2.5 text-sm text-slate-300 outline-none focus:border-blue-500">
                <option value="ALL">All assets</option>
                {assets.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
            </div>
          </div>

          {error && <div className="m-5 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</div>}

          <div className="overflow-x-auto">
            <table className="w-full min-w-[1050px] text-left text-sm">
              <thead className="border-b border-white/10 text-xs text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-medium">Type</th>
                  <th className="px-5 py-3 font-medium">Asset</th>
                  <th className="px-5 py-3 font-medium">Amount</th>
                  <th className="px-5 py-3 font-medium">Status</th>
                  <th className="px-5 py-3 font-medium">Reference</th>
                  <th className="px-5 py-3 text-right font-medium">Date</th>
                </tr>
              </thead>
              <tbody>
                {!loading && visible.map((item, index) => {
                  const itemAsset = String(item.asset ?? "ASSET").toUpperCase();
                  const direction = normalizeType(item.direction);
                  const type = normalizeType(item.type);
                  const status = normalizeType(item.status);

                  return (
                    <tr key={`${item.id}-${item.reference}-${index}`} className="border-b border-white/5 hover:bg-white/[0.025]">
                      <td className="px-5 py-4 font-medium">{type.charAt(0) + type.slice(1).toLowerCase()}</td>
                      <td className="px-5 py-4"><div className="flex items-center gap-3"><CoinIcon symbol={itemAsset} size={34} /><span className="font-semibold">{itemAsset}</span></div></td>
                      <td className={`px-5 py-4 font-semibold ${direction === "CREDIT" ? "text-emerald-400" : "text-red-400"}`}>{formatAmount(item.amount ?? 0, itemAsset, direction)}</td>
                      <td className="px-5 py-4"><span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-semibold text-emerald-400">{status || "UNKNOWN"}</span></td>
                      <td className="px-5 py-4 font-mono text-xs text-slate-500">{item.reference || "—"}</td>
                      <td className="px-5 py-4 text-right text-xs text-slate-400">{item.created_at ? formatDate(item.created_at) : "—"}</td>
                    </tr>
                  );
                })}
                {!loading && visible.length === 0 && <tr><td colSpan={6} className="px-5 py-16 text-center text-sm text-slate-500">No transactions match your filters.</td></tr>}
              </tbody>
            </table>
          </div>

          {loading && <div className="px-5 py-16 text-center text-sm text-slate-500">Loading transaction history...</div>}

          {!loading && (
            <div className="flex flex-col gap-3 border-t border-white/10 px-5 py-4 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between">
              <span>Showing {filtered.length === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1}–{Math.min(currentPage * PAGE_SIZE, filtered.length)} of {filtered.length} transactions</span>
              <div className="flex items-center gap-2">
                <button disabled={currentPage === 1} onClick={() => setPage((value) => Math.max(1, value - 1))} className="rounded-md border border-white/10 px-3 py-1.5 text-slate-400 disabled:cursor-not-allowed disabled:opacity-40 hover:text-white">Previous</button>
                <span className="px-2">Page {currentPage} of {totalPages}</span>
                <button disabled={currentPage === totalPages} onClick={() => setPage((value) => Math.min(totalPages, value + 1))} className="rounded-md border border-white/10 px-3 py-1.5 text-slate-400 disabled:cursor-not-allowed disabled:opacity-40 hover:text-white">Next</button>
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
