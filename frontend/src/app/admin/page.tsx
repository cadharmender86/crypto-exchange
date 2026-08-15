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

type Audit = {
  id: string;
  admin_user_id: string | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  result: string;
  created_at: string;
};

type KycResponse = { items: Array<{ id: string; status: string }>; total: number };

type KpiProps = {
  label: string;
  value: string;
  trend?: string;
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

function time(value: string) {
  return new Date(value).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
}

function KpiCard({ label, value, trend, note, icon, tone, spark: points }: KpiProps) {
  const line = points.map((point, index) => `${(index / (points.length - 1)) * 100},${100 - point}`).join(" ");
  return (
    <div className="relative overflow-hidden rounded-xl border border-slate-800 bg-[#0d1523] shadow-[0_10px_30px_rgba(0,0,0,.12)]">
      <div className="p-4 sm:p-5">
        <div className="flex items-start gap-3">
          <div className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl text-lg ${tone}`}>{icon}</div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium text-slate-400">{label}</p>
            <p className="mt-1 text-[27px] font-semibold tracking-tight text-white">{value}</p>
            <p className="mt-1 text-[11px] text-slate-500"><span className="font-semibold text-emerald-400">{trend || ""}</span>{trend ? " " : ""}{note}</p>
          </div>
        </div>
        <svg viewBox="0 0 100 35" preserveAspectRatio="none" className="mt-4 h-7 w-full opacity-90" aria-hidden="true">
          <polyline points={line} fill="none" stroke="currentColor" strokeWidth="1.5" className={tone.includes("indigo") ? "text-indigo-400" : tone.includes("emerald") ? "text-emerald-400" : tone.includes("amber") ? "text-amber-400" : "text-sky-400"} />
        </svg>
      </div>
      <div className="h-px bg-slate-800" />
      <div className="flex items-center justify-between px-4 py-2 text-[11px] text-slate-500"><span>{label === "Ledger Balance" ? "Total Assets" : "Count"}</span><span className="font-semibold text-slate-200">—</span></div>
    </div>
  );
}

function Section({ title, subtitle, children, className = "" }: { title: string; subtitle?: string; children: ReactNode; className?: string }) {
  return (
    <section className={`rounded-xl border border-slate-800 bg-[#0d1523] ${className}`}>
      <div className="flex items-center justify-between border-b border-slate-800/80 px-4 py-3.5 sm:px-5">
        <div><h3 className="text-sm font-semibold text-white">{title}</h3>{subtitle && <p className="mt-0.5 text-[10px] text-slate-500">{subtitle}</p>}</div>
      </div>
      {children}
    </section>
  );
}

function TradingChart() {
  const points = chart.map((value, index) => `${(index / (chart.length - 1)) * 100},${92 - value}`).join(" ");
  const area = `0,100 ${points} 100,100`;
  return (
    <Section title="Trading Volume (30 Days)">
      <div className="flex items-center justify-between px-4 pt-3 text-[10px] text-slate-500 sm:px-5"><span>₹10M</span><button className="rounded-md border border-slate-800 px-2.5 py-1 text-[10px] text-slate-300">30 Days⌄</button></div>
      <div className="relative h-48 px-4 pb-4 pt-2 sm:h-52 sm:px-5">
        <div className="absolute inset-x-5 top-4 bottom-6 flex flex-col justify-between opacity-60"><span className="border-t border-slate-800" /><span className="border-t border-slate-800" /><span className="border-t border-slate-800" /><span className="border-t border-slate-800" /><span className="border-t border-slate-800" /></div>
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="relative h-full w-full" aria-label="Trading volume chart">
          <polygon points={area} className="fill-indigo-500/15" />
          <polyline points={points} fill="none" stroke="currentColor" strokeWidth="1.4" className="text-indigo-500" />
        </svg>
        <div className="absolute inset-x-5 bottom-0 flex justify-between text-[10px] text-slate-600"><span>May 20</span><span>May 27</span><span>Jun 03</span><span>Jun 10</span><span>Jun 17</span></div>
      </div>
    </Section>
  );
}

function RiskAlerts({ kyc }: { kyc: number | null }) {
  return (
    <Section title="Risk & Alerts" subtitle="Compliance and operational attention">
      <div className="space-y-2 p-3 sm:p-4">
        <Link href="/admin/kyc" className="flex items-center gap-3 rounded-lg border border-amber-500/15 bg-amber-500/5 p-3 hover:border-amber-500/30">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-amber-500/10 text-amber-400">⚠</span><div className="min-w-0 flex-1"><p className="text-xs font-semibold text-slate-200">KYC Review Queue</p><p className="text-[10px] text-slate-500">{kyc == null ? "Loading verification queue" : `${kyc} applications pending review`}</p></div><span className="text-[11px] font-semibold text-indigo-400">Review Now</span>
        </Link>
        <Link href="/admin/audit" className="flex items-center gap-3 rounded-lg border border-rose-500/15 bg-rose-500/5 p-3 hover:border-rose-500/30">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-rose-500/10 text-rose-400">!</span><div className="min-w-0 flex-1"><p className="text-xs font-semibold text-slate-200">High Risk Transactions</p><p className="text-[10px] text-slate-500">Review flagged activity in Audit Logs</p></div><span className="text-[11px] font-semibold text-indigo-400">View All</span>
        </Link>
        <Link href="/admin/withdrawals" className="flex items-center gap-3 rounded-lg border border-sky-500/15 bg-sky-500/5 p-3 hover:border-sky-500/30">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-sky-500/10 text-sky-400">i</span><div className="min-w-0 flex-1"><p className="text-xs font-semibold text-slate-200">Pending Withdrawals</p><p className="text-[10px] text-slate-500">Review withdrawal approvals</p></div><span className="text-[11px] font-semibold text-indigo-400">View All</span>
        </Link>
      </div>
    </Section>
  );
}

function SystemHealth() {
  const services = ["API Status", "Database", "Blockchain Node", "Redis Cache", "Wallet Service"];
  return (
    <Section title="System Health" subtitle="Live operational dependencies">
      <div className="space-y-3 p-4 sm:p-5">
        {services.map((service) => <div key={service} className="flex items-center justify-between text-xs"><span className="flex items-center gap-2 text-slate-300"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />{service}</span><span className="flex items-center gap-2 text-emerald-300"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />Operational</span></div>)}
        <div className="border-t border-slate-800 pt-3 text-xs font-semibold text-emerald-400">✓ All systems operational</div>
      </div>
    </Section>
  );
}

function EmptyActivity({ title, href, description }: { title: string; href: string; description: string }) {
  return <div className="px-5 py-10 text-center"><p className="text-xs font-medium text-slate-400">{title}</p><p className="mt-1 text-[10px] text-slate-600">{description}</p><Link href={href} className="mt-3 inline-block text-[11px] font-semibold text-indigo-400 hover:text-indigo-300">Open management →</Link></div>;
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
          adminFetch("/api/v1/admin/audit-logs?limit=5"),
          adminFetch("/api/v1/admin/kyc?page=1&page_size=1"),
        ]);
        const dashboardData = (await dashboardResponse.json()) as Dashboard & { detail?: string };
        const auditData = (await auditResponse.json()) as Audit[] & { detail?: string };
        const kycData = (await kycResponse.json()) as KycResponse & { detail?: string };
        if (!dashboardResponse.ok) throw new Error(dashboardData.detail || "Unable to load dashboard");
        if (!auditResponse.ok) throw new Error(auditData.detail || "Unable to load audit activity");
        if (!kycResponse.ok) throw new Error(kycData.detail || "Unable to load KYC queue");
        setDashboard(dashboardData); setAudit(auditData); setKycTotal(kycData.total);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load dashboard");
      } finally { setLoading(false); }
    })();
  }, []);

  const kpis = useMemo<KpiProps[]>(() => [
    { label: "Total Users", value: loading ? "…" : number(dashboard?.total_users), trend: "", note: "registered accounts", icon: "♙", tone: "bg-indigo-500/15 text-indigo-400", spark },
    { label: "Active Users", value: loading ? "…" : number(dashboard?.active_users), trend: "", note: "currently active accounts", icon: "♙", tone: "bg-emerald-500/15 text-emerald-400", spark: spark.map((v, i) => v + (i % 4)) },
    { label: "KYC Pending", value: loading ? "…" : number(kycTotal), trend: "", note: "applications requiring review", icon: "♙", tone: "bg-amber-500/15 text-amber-400", spark: spark.map((v, i) => v - (i % 5)) },
    { label: "KYC Verified", value: loading ? "…" : number(dashboard?.verified_users), trend: "", note: "verified customers", icon: "◈", tone: "bg-sky-500/15 text-sky-400", spark },
    { label: "Total Deposits", value: "—", note: "volume will appear when API is exposed", icon: "$", tone: "bg-emerald-500/15 text-emerald-400", spark },
    { label: "Total Withdrawals", value: "—", note: "volume will appear when API is exposed", icon: "↗", tone: "bg-rose-500/15 text-rose-400", spark },
    { label: "Trading Volume", value: "—", note: "order analytics will appear when API is exposed", icon: "⌁", tone: "bg-sky-500/15 text-sky-400", spark },
    { label: "Ledger Balance", value: "—", note: "accounting aggregate will appear when API is exposed", icon: "◉", tone: "bg-amber-500/15 text-amber-400", spark },
  ], [dashboard, kycTotal, loading]);

  return (
    <div className="mx-auto max-w-[1320px] space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div><p className="text-2xl font-semibold tracking-tight text-white">Dashboard</p><p className="mt-1 text-sm text-slate-400">Welcome back, Super Admin</p></div>
        <button className="flex items-center gap-2 self-start rounded-lg border border-slate-800 bg-[#0d1523] px-3 py-2 text-xs font-medium text-slate-300 hover:border-slate-700 sm:self-auto">▣ May 20, 2025 — Jun 19, 2025 <span className="text-slate-600">⌄</span></button>
      </div>

      {error && <div className="rounded-lg border border-rose-500/20 bg-rose-500/5 px-4 py-3 text-xs text-rose-300">{error}</div>}

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((item) => <KpiCard key={item.label} {...item} />)}
      </div>

      <div className="grid gap-3 xl:grid-cols-[1.55fr_1fr_1fr]">
        <TradingChart />
        <RiskAlerts kyc={kycTotal} />
        <SystemHealth />
      </div>

      <div className="grid gap-3 xl:grid-cols-2">
        <Section title="Recent Deposits"><EmptyActivity title="Deposit activity" href="/admin/deposits" description="Recent deposit data will be connected to the admin deposits API." /></Section>
        <Section title="Recent Withdrawals"><EmptyActivity title="Withdrawal activity" href="/admin/withdrawals" description="Recent withdrawal data will be connected to the admin withdrawals API." /></Section>
      </div>

      <Section title="Recent Admin Activity" subtitle="Audit events from the backend">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[680px] text-left text-xs">
            <thead className="border-b border-slate-800 text-[10px] uppercase tracking-wider text-slate-500"><tr><th className="px-5 py-3">Action</th><th className="py-3">Resource</th><th className="py-3">Result</th><th className="py-3 pr-5">Time</th></tr></thead>
            <tbody>{loading ? <tr><td colSpan={4} className="py-8 text-center text-slate-500">Loading activity…</td></tr> : audit.length === 0 ? <tr><td colSpan={4} className="py-8 text-center text-slate-500">No audit activity yet.</td></tr> : audit.map((item) => <tr key={item.id} className="border-b border-slate-800/70 last:border-0"><td className="px-5 py-3 font-medium text-slate-200">{item.action}</td><td className="py-3 text-slate-400">{item.resource_type}{item.resource_id ? ` · ${item.resource_id.slice(0, 8)}` : ""}</td><td className={`py-3 font-semibold ${item.result === "SUCCESS" ? "text-emerald-400" : "text-rose-400"}`}>{item.result}</td><td className="py-3 pr-5 text-slate-500">{time(item.created_at)}</td></tr>)}</tbody>
          </table>
        </div>
      </Section>

      <footer className="flex flex-col justify-between gap-2 border-t border-slate-800/80 pt-4 text-[10px] text-slate-600 sm:flex-row"><span>© 2026 BitNova Exchange Admin Panel. All rights reserved.</span><span>Version 1.0.0</span></footer>
    </div>
  );
}
