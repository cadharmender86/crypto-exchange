"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { adminFetch } from "@/lib/adminApi";

type Dashboard = {
  total_users: number;
  active_users: number;
  verified_users: number;
};

type KycResponse = { items: Array<{ id: string; status: string }>; total: number };

type TransactionRow = {
  id: string;
  user_email: string;
  network: string;
  amount: string;
  status: string;
  created_at: string;
  blockchain_tx_hash?: string;
  confirmations?: number;
  destination_address?: string;
};

type TransactionList = {
  items: TransactionRow[];
  total: number;
};

type KpiProps = {
  label: string;
  value: string;
  note: string;
  icon: string;
  tone: string;
  spark: number[];
};

const spark = [20, 26, 17, 24, 21, 30, 24, 35, 28, 39, 31, 44, 34, 47, 39, 51, 43, 55];
const chart = [42, 48, 39, 53, 45, 50, 61, 58, 68, 64, 74, 71, 82, 77, 69, 86, 78, 91, 84, 88];

function number(value: number | null | undefined) {
  return value == null ? "—" : value.toLocaleString();
}

function formatTime(value: string) {
  return new Date(value).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}

function statusClass(status: string) {
  if (["APPROVED", "CONFIRMED", "COMPLETED"].includes(status)) return "bg-emerald-500/10 text-emerald-300";
  if (["REJECTED", "FAILED"].includes(status)) return "bg-rose-500/10 text-rose-300";
  return "bg-amber-500/10 text-amber-300";
}

function Section({ title, subtitle, children, className = "" }: { title: string; subtitle?: string; children: ReactNode; className?: string }) {
  return (
    <section className={`overflow-hidden rounded-xl border border-slate-800 bg-[#0d1523] ${className}`}>
      <div className="flex items-center justify-between border-b border-slate-800/80 px-4 py-3 sm:px-5">
        <div>
          <h3 className="text-sm font-semibold text-white">{title}</h3>
          {subtitle && <p className="mt-0.5 text-[10px] text-slate-500">{subtitle}</p>}
        </div>
      </div>
      {children}
    </section>
  );
}

function KpiCard({ label, value, note, icon, tone, spark: points }: KpiProps) {
  const line = points.map((point, index) => `${(index / (points.length - 1)) * 100},${100 - point}`).join(" ");
  const lineTone = tone.includes("indigo") ? "text-indigo-400" : tone.includes("emerald") ? "text-emerald-400" : tone.includes("amber") ? "text-amber-400" : "text-sky-400";

  return (
    <div className="relative overflow-hidden rounded-xl border border-slate-800 bg-[#0d1523] shadow-[0_8px_25px_rgba(0,0,0,.1)]">
      <div className="p-3.5 sm:p-4">
        <div className="flex items-start gap-3">
          <div className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg text-sm ${tone}`}>{icon}</div>
          <div className="min-w-0 flex-1">
            <p className="text-[11px] font-medium text-slate-400">{label}</p>
            <p className="mt-0.5 text-[26px] font-semibold tracking-tight text-white">{value}</p>
            <p className="mt-1 min-h-8 text-[10px] leading-4 text-slate-500">{note}</p>
          </div>
        </div>
        <svg viewBox="0 0 100 30" preserveAspectRatio="none" className={`mt-2 h-6 w-full opacity-90 ${lineTone}`} aria-hidden="true">
          <polyline points={line} fill="none" stroke="currentColor" strokeWidth="1.5" />
        </svg>
      </div>
      <div className="flex items-center justify-between border-t border-slate-800 px-3.5 py-2 text-[10px] text-slate-500 sm:px-4">
        <span>{label === "Ledger Balance" ? "Total Assets" : "Count"}</span>
        <span className="font-semibold text-slate-200">—</span>
      </div>
    </div>
  );
}

function TradingChart() {
  const points = chart.map((value, index) => `${(index / (chart.length - 1)) * 100},${92 - value}`).join(" ");
  return (
    <Section title="Trading Volume (30 Days)">
      <div className="flex items-center justify-between px-4 pt-3 text-[10px] text-slate-500 sm:px-5">
        <span>₹10M</span>
        <button className="rounded-md border border-slate-800 px-2.5 py-1 text-[10px] text-slate-300">30 Days⌄</button>
      </div>
      <div className="relative h-48 px-4 pb-4 pt-2 sm:h-52 sm:px-5">
        <div className="absolute inset-x-5 top-4 bottom-6 flex flex-col justify-between opacity-60">
          {[0, 1, 2, 3, 4].map((item) => <span key={item} className="border-t border-slate-800" />)}
        </div>
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="relative h-full w-full" aria-label="Trading volume chart">
          <polygon points={`0,100 ${points} 100,100`} className="fill-indigo-500/15" />
          <polyline points={points} fill="none" stroke="currentColor" strokeWidth="1.4" className="text-indigo-500" />
        </svg>
        <div className="absolute inset-x-5 bottom-0 flex justify-between text-[9px] text-slate-600"><span>May 20</span><span>May 27</span><span>Jun 03</span><span>Jun 10</span><span>Jun 17</span></div>
      </div>
    </Section>
  );
}

function RiskAlerts({ kyc }: { kyc: number | null }) {
  const alerts = [
    { title: "KYC Review Queue", text: kyc == null ? "Loading verification queue" : `${kyc} applications pending review`, href: "/admin/kyc", icon: "⚠", tone: "amber" },
    { title: "High Risk Transactions", text: "Review flagged activity in Audit Logs", href: "/admin/audit", icon: "!", tone: "rose" },
    { title: "Pending Withdrawals", text: "Review withdrawal approvals", href: "/admin/withdrawals", icon: "i", tone: "sky" },
  ];
  return (
    <Section title="Risk & Alerts" subtitle="Compliance and operational attention">
      <div className="space-y-2 p-3 sm:p-4">
        {alerts.map((alert) => (
          <Link key={alert.title} href={alert.href} className={`flex items-center gap-3 rounded-lg border p-3 hover:border-slate-700 ${alert.tone === "amber" ? "border-amber-500/15 bg-amber-500/5" : alert.tone === "rose" ? "border-rose-500/15 bg-rose-500/5" : "border-sky-500/15 bg-sky-500/5"}`}>
            <span className={`grid h-8 w-8 place-items-center rounded-lg ${alert.tone === "amber" ? "bg-amber-500/10 text-amber-400" : alert.tone === "rose" ? "bg-rose-500/10 text-rose-400" : "bg-sky-500/10 text-sky-400"}`}>{alert.icon}</span>
            <div className="min-w-0 flex-1"><p className="text-[11px] font-semibold text-slate-200">{alert.title}</p><p className="text-[9px] text-slate-500">{alert.text}</p></div>
            <span className="whitespace-nowrap text-[10px] font-semibold text-indigo-400">{alert.tone === "amber" ? "Review Now" : "View All"}</span>
          </Link>
        ))}
      </div>
    </Section>
  );
}

function SystemHealth() {
  const services = ["API Status", "Database", "Blockchain Node", "Redis Cache", "Wallet Service"];
  return (
    <Section title="System Health" subtitle="Live operational dependencies">
      <div className="space-y-2.5 p-4 sm:p-5">
        {services.map((service) => <div key={service} className="flex items-center justify-between text-[10px]"><span className="flex items-center gap-2 text-slate-300"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />{service}</span><span className="flex items-center gap-2 text-emerald-300"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />Operational</span></div>)}
        <div className="border-t border-slate-800 pt-2.5 text-[10px] font-semibold text-emerald-400">✓ All systems operational</div>
      </div>
    </Section>
  );
}

function ActivityTable({ title, href, rows, loading, type }: { title: string; href: string; rows: TransactionRow[]; loading: boolean; type: "deposits" | "withdrawals" }) {
  return (
    <Section title={title}>
      <div className="flex items-center justify-end border-b border-slate-800/70 px-4 py-2.5 sm:px-5">
        <Link href={href} className="text-[10px] font-semibold text-indigo-400 hover:text-indigo-300">View All →</Link>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] text-left text-[10px]">
          <thead className="border-b border-slate-800 text-[9px] uppercase tracking-wider text-slate-500">
            <tr>
              <th className="px-4 py-2.5 sm:px-5">ID</th>
              <th className="py-2.5">User</th>
              <th className="py-2.5">Asset</th>
              <th className="py-2.5">Amount</th>
              <th className="py-2.5">Status</th>
              <th className="py-2.5 pr-4">Time</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="px-5 py-8 text-center text-slate-500">Loading...</td></tr>
            ) : rows.length === 0 ? (
              <tr><td colSpan={6} className="px-5 py-8 text-center text-slate-500">No recent {type} found.</td></tr>
            ) : (
              rows.slice(0, 5).map((row) => (
                <tr key={row.id} className="border-b border-slate-800/70 last:border-0">
                  <td className="px-4 py-3 font-medium text-slate-300 sm:px-5">{row.id.slice(0, 12)}</td>
                  <td className="max-w-[170px] truncate py-3 pr-3 text-slate-400">{row.user_email}</td>
                  <td className="py-3 pr-3 text-slate-300"><span className="mr-1.5 inline-block h-4 w-4 rounded-full bg-emerald-500/15 text-center text-[8px] leading-4 text-emerald-300">{row.network.slice(0, 1).toUpperCase()}</span>{row.network}</td>
                  <td className="py-3 pr-3 font-medium text-slate-200">{row.amount}</td>
                  <td className="py-3 pr-3"><span className={`rounded-md px-2 py-1 ${statusClass(row.status)}`}>{row.status.replaceAll("_", " ")}</span></td>
                  <td className="py-3 pr-4 whitespace-nowrap text-slate-500">{formatTime(row.created_at)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Section>
  );
}

export default function AdminDashboard() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [kycTotal, setKycTotal] = useState<number | null>(null);
  const [deposits, setDeposits] = useState<TransactionRow[]>([]);
  const [withdrawals, setWithdrawals] = useState<TransactionRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [dashboardResponse, kycResponse, depositsResponse, withdrawalsResponse] = await Promise.all([
          adminFetch("/api/v1/admin/dashboard"),
          adminFetch("/api/v1/admin/kyc?page=1&page_size=1"),
          adminFetch("/api/v1/admin/deposits?page=1&page_size=5"),
          adminFetch("/api/v1/admin/withdrawals?page=1&page_size=5"),
        ]);

        const dashboardData = (await dashboardResponse.json()) as Dashboard & { detail?: string };
        const kycData = (await kycResponse.json()) as KycResponse & { detail?: string };
        const depositsData = (await depositsResponse.json()) as TransactionList & { detail?: string };
        const withdrawalsData = (await withdrawalsResponse.json()) as TransactionList & { detail?: string };

        if (!dashboardResponse.ok) throw new Error(dashboardData.detail || "Unable to load dashboard");
        if (!kycResponse.ok) throw new Error(kycData.detail || "Unable to load KYC queue");
        if (!depositsResponse.ok) throw new Error(depositsData.detail || "Unable to load deposits");
        if (!withdrawalsResponse.ok) throw new Error(withdrawalsData.detail || "Unable to load withdrawals");

        setDashboard(dashboardData);
        setKycTotal(kycData.total);
        setDeposits(depositsData.items || []);
        setWithdrawals(withdrawalsData.items || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load dashboard");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const kpis = useMemo<KpiProps[]>(() => [
    { label: "Total Users", value: loading ? "…" : number(dashboard?.total_users), note: "registered accounts", icon: "♙", tone: "bg-indigo-500/15 text-indigo-400", spark },
    { label: "Active Users", value: loading ? "…" : number(dashboard?.active_users), note: "currently active accounts", icon: "♙", tone: "bg-emerald-500/15 text-emerald-400", spark: spark.map((v, i) => v + (i % 4)) },
    { label: "KYC Pending", value: loading ? "…" : number(kycTotal), note: "applications requiring review", icon: "♙", tone: "bg-amber-500/15 text-amber-400", spark: spark.map((v, i) => v - (i % 5)) },
    { label: "KYC Verified", value: loading ? "…" : number(dashboard?.verified_users), note: "verified customers", icon: "◈", tone: "bg-sky-500/15 text-sky-400", spark },
    { label: "Total Deposits", value: "—", note: "volume will appear when API is exposed", icon: "$", tone: "bg-emerald-500/15 text-emerald-400", spark },
    { label: "Total Withdrawals", value: "—", note: "volume will appear when API is exposed", icon: "↗", tone: "bg-rose-500/15 text-rose-400", spark },
    { label: "Trading Volume", value: "—", note: "order analytics will appear when API is exposed", icon: "⌁", tone: "bg-sky-500/15 text-sky-400", spark },
    { label: "Ledger Balance", value: "—", note: "accounting aggregate will appear when API is exposed", icon: "◉", tone: "bg-amber-500/15 text-amber-400", spark },
  ], [dashboard, kycTotal, loading]);

  return (
    <div className="w-full space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div><p className="text-2xl font-semibold tracking-tight text-white">Dashboard</p><p className="mt-1 text-sm text-slate-400">Welcome back, Super Admin</p></div>
        <button className="flex items-center gap-2 self-start rounded-lg border border-slate-800 bg-[#0d1523] px-3 py-2 text-[10px] font-medium text-slate-300 hover:border-slate-700 sm:self-auto">▣ May 20, 2025 — Jun 19, 2025 <span className="text-slate-600">⌄</span></button>
      </div>

      {error && <div className="rounded-lg border border-rose-500/20 bg-rose-500/5 px-4 py-3 text-xs text-rose-300">{error}</div>}

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((item) => <KpiCard key={item.label} {...item} />)}
      </div>

      <div className="grid gap-3 xl:grid-cols-[1.7fr_1fr_1fr]">
        <TradingChart />
        <RiskAlerts kyc={kycTotal} />
        <SystemHealth />
      </div>

      <div className="grid gap-3 xl:grid-cols-2">
        <ActivityTable title="Recent Deposits" href="/admin/deposits" rows={deposits} loading={loading} type="deposits" />
        <ActivityTable title="Recent Withdrawals" href="/admin/withdrawals" rows={withdrawals} loading={loading} type="withdrawals" />
      </div>

      <footer className="flex flex-col gap-2 border-t border-slate-800 pt-4 text-[10px] text-slate-500 sm:flex-row sm:items-center sm:justify-between">
        <span>© 2026 BitNova Exchange Admin Panel. All rights reserved.</span>
        <span>Version 1.0.0</span>
      </footer>
    </div>
  );
}
