"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { adminFetch } from "@/lib/adminApi";

type Dashboard = {
  total_users: number;
  active_users: number;
  verified_users: number;
};

type Audit = {
  id: string;
  admin_user_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  result: string;
  reason: string | null;
  created_at: string;
};

type KycResponse = {
  items: Array<{ id: string; status: string }>;
  total: number;
};

function formatNumber(value: number | undefined) {
  return value === undefined ? "—" : value.toLocaleString();
}

function formatTime(value: string) {
  return new Date(value).toLocaleString();
}

function MetricCard({
  label,
  value,
  caption,
  tone,
}: {
  label: string;
  value: string;
  caption: string;
  tone: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5 shadow-[0_12px_35px_rgba(0,0,0,0.12)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          <p className={`mt-3 text-2xl font-bold tracking-tight ${tone}`}>{value}</p>
        </div>
        <div className="h-2.5 w-2.5 rounded-full bg-current opacity-70" />
      </div>
      <p className="mt-3 text-xs text-slate-600">{caption}</p>
    </div>
  );
}

export default function AdminDashboard() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [kycTotal, setKycTotal] = useState<number | null>(null);
  const [audit, setAudit] = useState<Audit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [dashboardResponse, auditResponse, kycResponse] = await Promise.all([
          adminFetch("/api/v1/admin/dashboard"),
          adminFetch("/api/v1/admin/audit-logs?limit=8"),
          adminFetch("/api/v1/admin/kyc?page=1&page_size=1"),
        ]);

        const dashboardData = (await dashboardResponse.json()) as Dashboard & { detail?: string };
        const auditData = (await auditResponse.json()) as Audit[] & { detail?: string };
        const kycData = (await kycResponse.json()) as KycResponse & { detail?: string };

        if (!dashboardResponse.ok) {
          throw new Error(dashboardData.detail || "Unable to load dashboard");
        }
        if (!auditResponse.ok) {
          throw new Error(auditData.detail || "Unable to load audit activity");
        }
        if (!kycResponse.ok) {
          throw new Error(kycData.detail || "Unable to load KYC queue");
        }

        setDashboard(dashboardData);
        setAudit(auditData);
        setKycTotal(kycData.total);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load dashboard");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div className="mx-auto max-w-7xl space-y-7">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-sm font-medium text-cyan-400">Admin operations</p>
          <h2 className="mt-1 text-2xl font-bold tracking-tight text-slate-100">Exchange overview</h2>
          <p className="mt-2 text-sm text-slate-500">
            Monitor customers, compliance, funds and operational activity from one place.
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            href="/admin/kyc"
            className="rounded-xl bg-cyan-500 px-4 py-2.5 text-sm font-bold text-slate-950 transition hover:bg-cyan-400"
          >
            Review KYC queue
          </Link>
          <Link
            href="/admin/audit"
            className="rounded-xl border border-slate-700 px-4 py-2.5 text-sm font-semibold text-slate-300 transition hover:border-slate-500"
          >
            Audit log
          </Link>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Total users"
          value={loading ? "…" : formatNumber(dashboard?.total_users)}
          caption="Registered customer accounts"
          tone="text-cyan-300"
        />
        <MetricCard
          label="Active users"
          value={loading ? "…" : formatNumber(dashboard?.active_users)}
          caption="Currently active accounts"
          tone="text-emerald-300"
        />
        <MetricCard
          label="KYC queue"
          value={loading ? "…" : formatNumber(kycTotal ?? undefined)}
          caption="Verification records requiring attention"
          tone="text-amber-300"
        />
        <MetricCard
          label="Verified users"
          value={loading ? "…" : formatNumber(dashboard?.verified_users)}
          caption="Customers with verified status"
          tone="text-violet-300"
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.55fr_1fr]">
        <section className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-slate-100">Trading & funds overview</h3>
              <p className="mt-1 text-xs text-slate-500">Operational areas ready for live exchange metrics</p>
            </div>
            <span className="rounded-full border border-slate-700 px-2.5 py-1 text-[11px] font-semibold text-slate-500">
              Live APIs
            </span>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <Link
              href="/admin/deposits"
              className="group rounded-xl border border-slate-800 bg-slate-950/30 p-5 transition hover:border-cyan-500/30"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-200">Deposits</span>
                <span className="text-slate-600 transition group-hover:text-cyan-400">→</span>
              </div>
              <p className="mt-3 text-2xl font-bold text-slate-300">—</p>
              <p className="mt-1 text-xs text-slate-600">Deposit volume metric will appear when the dashboard API exposes it.</p>
            </Link>

            <Link
              href="/admin/withdrawals"
              className="group rounded-xl border border-slate-800 bg-slate-950/30 p-5 transition hover:border-amber-500/30"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-200">Withdrawals</span>
                <span className="text-slate-600 transition group-hover:text-amber-400">→</span>
              </div>
              <p className="mt-3 text-2xl font-bold text-slate-300">—</p>
              <p className="mt-1 text-xs text-slate-600">Withdrawal volume and pending approvals.</p>
            </Link>

            <Link
              href="/admin/orders"
              className="group rounded-xl border border-slate-800 bg-slate-950/30 p-5 transition hover:border-violet-500/30"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-200">Trading volume</span>
                <span className="text-slate-600 transition group-hover:text-violet-400">→</span>
              </div>
              <p className="mt-3 text-2xl font-bold text-slate-300">—</p>
              <p className="mt-1 text-xs text-slate-600">Order and execution analytics will be connected here.</p>
            </Link>

            <Link
              href="/admin/ledger"
              className="group rounded-xl border border-slate-800 bg-slate-950/30 p-5 transition hover:border-emerald-500/30"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-200">Ledger</span>
                <span className="text-slate-600 transition group-hover:text-emerald-400">→</span>
              </div>
              <p className="mt-3 text-2xl font-bold text-slate-300">Operational</p>
              <p className="mt-1 text-xs text-slate-600">Open the accounting ledger and transaction trail.</p>
            </Link>
          </div>
        </section>

        <section className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-slate-100">Risk & alerts</h3>
              <p className="mt-1 text-xs text-slate-500">Compliance and operational attention</p>
            </div>
            <span className="text-amber-400">⚠</span>
          </div>

          <div className="mt-5 space-y-3">
            <Link href="/admin/kyc" className="flex items-center justify-between rounded-xl border border-amber-500/15 bg-amber-500/5 p-4 hover:border-amber-500/30">
              <div>
                <p className="text-sm font-semibold text-slate-200">KYC review queue</p>
                <p className="mt-1 text-xs text-slate-500">Verification cases awaiting action</p>
              </div>
              <span className="text-lg font-bold text-amber-300">{loading ? "…" : formatNumber(kycTotal ?? undefined)}</span>
            </Link>
            <Link href="/admin/audit" className="flex items-center justify-between rounded-xl border border-red-500/15 bg-red-500/5 p-4 hover:border-red-500/30">
              <div>
                <p className="text-sm font-semibold text-slate-200">Audit monitoring</p>
                <p className="mt-1 text-xs text-slate-500">Review administrative actions</p>
              </div>
              <span className="text-red-300">View →</span>
            </Link>
            <Link href="/admin/withdrawals" className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/30 p-4 hover:border-slate-700">
              <div>
                <p className="text-sm font-semibold text-slate-200">Withdrawal controls</p>
                <p className="mt-1 text-xs text-slate-500">Review and manage withdrawal operations</p>
              </div>
              <span className="text-slate-500">View →</span>
            </Link>
          </div>
        </section>
      </div>

      <section className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-slate-100">Recent admin activity</h3>
            <p className="mt-1 text-xs text-slate-500">Audit events from the backend</p>
          </div>
          <Link href="/admin/audit" className="text-xs font-semibold text-cyan-400 hover:text-cyan-300">View all →</Link>
        </div>
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead className="border-b border-slate-800 text-xs uppercase tracking-wider text-slate-500">
              <tr>
                <th className="pb-3 pr-4">Action</th>
                <th className="pb-3 pr-4">Resource</th>
                <th className="pb-3 pr-4">Result</th>
                <th className="pb-3">Time</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={4} className="py-10 text-center text-slate-500">Loading activity...</td></tr>
              ) : audit.length === 0 ? (
                <tr><td colSpan={4} className="py-10 text-center text-slate-500">No audit activity yet.</td></tr>
              ) : (
                audit.map((item) => (
                  <tr key={item.id} className="border-b border-slate-800/70 last:border-0">
                    <td className="py-4 pr-4 font-medium text-slate-200">{item.action}</td>
                    <td className="py-4 pr-4 text-slate-400">{item.resource_type}{item.resource_id ? ` · ${item.resource_id.slice(0, 8)}` : ""}</td>
                    <td className="py-4 pr-4 text-emerald-300">{item.result}</td>
                    <td className="py-4 text-slate-500">{formatTime(item.created_at)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
