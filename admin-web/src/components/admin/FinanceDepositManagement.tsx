"use client";

import { useEffect, useState } from "react";
import { getFiatDeposits } from "@/lib/adminApi";
import type { FiatDepositListItem } from "@/lib/types/admin";

export default function FinanceDepositManagement() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deposits, setDeposits] = useState<FiatDepositListItem[]>([]);

  useEffect(() => {
    loadDeposits();
  }, []);

  async function loadDeposits() {
    try {
      setLoading(true);
      setError("");

      const response = await getFiatDeposits({
        limit: 20,
        offset: 0,
      });

      setDeposits(Array.isArray(response.items) ? response.items : []);
    } catch (err: any) {
      setError(err instanceof Error ? err.message : "Failed to load deposits.");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <p className="text-slate-400">Loading fiat deposits...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-900 bg-red-950 p-6 text-red-400">
        {error}
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-slate-950 text-slate-400 uppercase text-xs">
          <tr>
            <th className="px-4 py-3 text-left">User</th>
            <th className="px-4 py-3 text-left">Bank</th>
            <th className="px-4 py-3 text-left">UTR</th>
            <th className="px-4 py-3 text-left">Amount</th>
            <th className="px-4 py-3 text-left">Status</th>
            <th className="px-4 py-3 text-left">Created</th>
            <th className="px-4 py-3 text-right">Action</th>
          </tr>
        </thead>

        <tbody>
          {deposits.length === 0 ? (
            <tr>
              <td colSpan={7} className="py-10 text-center text-slate-500">
                No fiat deposits found.
              </td>
            </tr>
          ) : (
            deposits.map((deposit) => (
              <tr
                key={deposit.id}
                className="border-t border-slate-800 hover:bg-slate-800/40"
              >
                <td className="px-4 py-3">
                  <div className="font-medium text-white">
                    {deposit.user_name}
                  </div>
                  <div className="text-xs text-slate-400">
                    {deposit.user_email}
                  </div>
                </td>

                <td className="px-4 py-3 text-slate-300">
                  {deposit.bank_name}
                </td>

                <td className="px-4 py-3 font-mono text-slate-300">
                  {deposit.utr_number}
                </td>

                <td className="px-4 py-3 text-emerald-400 font-semibold">
                  ₹ {Number(deposit.amount).toLocaleString("en-IN", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                })}
                </td>

                <td className="px-4 py-3">
                  <span className="rounded-full bg-yellow-500/20 px-2 py-1 text-xs text-yellow-300">
                    {deposit.status}
                  </span>
                </td>

                <td className="px-4 py-3 text-slate-400">
                  {new Date(deposit.created_at).toLocaleString()}
                </td>

                <td className="px-4 py-3 text-right">
                  <button className="rounded-lg border border-slate-700 px-3 py-1 text-xs text-white hover:bg-slate-700">
                    View
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}