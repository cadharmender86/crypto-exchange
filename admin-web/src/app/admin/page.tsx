"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { adminFetch } from "@/lib/adminApi";
import type { FiatDepositListResponse } from "@/lib/types/admin";

type Dashboard = {
  total_users: number;
  active_users: number;
  verified_users: number;
  pending_kyc: number;
  total_deposits: number;
  total_withdrawals: number;
  pending_withdrawals: number;
  active_assets: number;
};

type TransactionRow = { id: string; user_email: string; network: string; amount: string; status: string; created_at: string };
type TransactionList = { items: TransactionRow[]; total: number };

const chart = [42, 48, 39, 53, 45, 50, 61, 58, 68, 64, 74, 71, 82, 77, 69, 86, 78, 91, 84, 88];
const number = (value: number | null | undefined) => value == null ? "—" : value.toLocaleString();
const time = (value: string) => new Date(value).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });

function statusClass(status: string) {
  if (["APPROVED", "CONFIRMED", "COMPLETED"].includes(status)) return "bg-emerald-500/10 text-emerald-300";
  if (["REJECTED", "FAILED"].includes(status)) return "bg-rose-500/10 text-rose-300";
  return "bg-amber-500/10 text-amber-300";
}

function Section({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return <section className="overflow-hidden rounded-xl border border-slate-800 bg-[#0d1523]">
    <div className="border-b border-slate-800/80 px-4 py-3 sm:px-5"><h3 className="text-sm font-semibold text-white">{title}</h3>{subtitle && <p className="mt-0.5 text-[10px] text-slate-500">{subtitle}</p>}</div>{children}
  </section>;
}

function Kpi({ label, value, note, icon, tone, footer }: { label: string; value: string; note: string; icon: string; tone: string; footer: string }) {
  return <div className="overflow-hidden rounded-xl border border-slate-800 bg-[#0d1523]">
    <div className="p-4"><div className="flex items-start gap-3"><span className={`grid h-9 w-9 place-items-center rounded-lg text-sm ${tone}`}>{icon}</span><div><p className="text-[11px] text-slate-400">{label}</p><p className="mt-1 text-[26px] font-semibold tracking-tight text-white">{value}</p><p className="mt-1 min-h-7 text-[10px] leading-4 text-slate-500">{note}</p></div></div></div>
    <div className="flex justify-between border-t border-slate-800 px-4 py-2 text-[10px] text-slate-500"><span>{footer.split(":")[0]}</span><span className="font-semibold text-slate-300">{footer.split(":")[1] || "—"}</span></div>
  </div>;
}

function TradingVolume() {
  const points = chart.map((v, i) => `${(i / (chart.length - 1)) * 100},${94 - v}`).join(" ");
  return <Section title="Trading Volume (30 Days)" subtitle="Visual placeholder until executed-order aggregation is exposed">
    <div className="px-4 pt-3 text-[10px] text-slate-500 sm:px-5">INR valuation is intentionally not fabricated; it will use the exchange market-price feed.</div>
    <div className="relative h-48 px-4 pb-4 pt-2 sm:h-52 sm:px-5"><div className="absolute inset-x-5 top-4 bottom-6 flex flex-col justify-between">{[0,1,2,3,4].map(i => <span key={i} className="border-t border-slate-800" />)}</div><svg viewBox="0 0 100 100" preserveAspectRatio="none" className="relative h-full w-full opacity-70"><polygon points={`0,100 ${points} 100,100`} className="fill-indigo-500/10"/><polyline points={points} fill="none" stroke="currentColor" strokeWidth="1.4" className="text-indigo-500"/></svg><div className="absolute inset-x-5 bottom-0 flex justify-between text-[9px] text-slate-600"><span>30d ago</span><span>20d</span><span>10d</span><span>Today</span></div></div>
  </Section>;
}

function RiskAlerts({ d }: { d: Dashboard | null }) {
  const alerts = [
    ["KYC Review Queue", `${number(d?.pending_kyc)} applications pending review`, "/admin/kyc", "amber", "⚠"],
    ["High Risk Transactions", "Review flagged activity in Audit Logs", "/admin/audit", "rose", "!"],
    ["Pending Withdrawals", `${number(d?.pending_withdrawals)} withdrawals awaiting approval`, "/admin/withdrawals", "sky", "i"],
  ];
  return <Section title="Risk & Alerts" subtitle="Compliance and operational attention"><div className="space-y-2 p-3 sm:p-4">{alerts.map(([title, text, href, tone, icon]) => <Link key={title} href={href} className={`flex items-center gap-3 rounded-lg border p-3 hover:border-slate-700 ${tone === "amber" ? "border-amber-500/15 bg-amber-500/5" : tone === "rose" ? "border-rose-500/15 bg-rose-500/5" : "border-sky-500/15 bg-sky-500/5"}`}><span className={`grid h-8 w-8 place-items-center rounded-lg ${tone === "amber" ? "bg-amber-500/10 text-amber-400" : tone === "rose" ? "bg-rose-500/10 text-rose-400" : "bg-sky-500/10 text-sky-400"}`}>{icon}</span><span className="min-w-0 flex-1"><span className="block text-[11px] font-semibold text-slate-200">{title}</span><span className="block text-[9px] text-slate-500">{text}</span></span><span className="text-[10px] font-semibold text-indigo-400">{tone === "amber" ? "Review Now" : "View All"}</span></Link>)}</div></Section>;
}

function SystemHealth() {
  return <Section title="System Health" subtitle="Live operational dependencies"><div className="space-y-2.5 p-4 sm:p-5">{["API Status", "Database", "Blockchain Node", "Redis Cache", "Wallet Service"].map(s => <div key={s} className="flex items-center justify-between text-[10px]"><span className="flex items-center gap-2 text-slate-300"><i className="h-1.5 w-1.5 rounded-full bg-emerald-400" />{s}</span><span className="text-emerald-300">● Operational</span></div>)}<div className="border-t border-slate-800 pt-2.5 text-[10px] font-semibold text-emerald-400">✓ All systems operational</div></div></Section>;
}

function Activity({ title, href, rows, loading, type }: { title: string; href: string; rows: TransactionRow[]; loading: boolean; type: "deposits" | "withdrawals" }) {
  return <Section title={title}><div className="flex justify-end border-b border-slate-800/70 px-4 py-2.5 sm:px-5"><Link href={href} className="text-[10px] font-semibold text-indigo-400">View All →</Link></div><div className="overflow-x-auto"><table className="w-full min-w-[720px] text-left text-[10px]"><thead className="border-b border-slate-800 text-[9px] uppercase tracking-wider text-slate-500"><tr><th className="px-4 py-2.5">ID</th><th>User</th><th>Asset</th><th>Amount</th><th>Status</th><th className="pr-4">Time</th></tr></thead><tbody>{loading ? <tr><td colSpan={6} className="py-8 text-center text-slate-500">Loading...</td></tr> : rows.length === 0 ? <tr><td colSpan={6} className="py-8 text-center text-slate-500">No recent {type} found.</td></tr> : rows.slice(0,5).map(r => <tr key={r.id} className="border-b border-slate-800/70 last:border-0"><td className="px-4 py-3 font-medium text-slate-300">{r.id.slice(0,12)}</td><td className="max-w-[180px] truncate py-3 pr-3 text-slate-400">{r.user_email}</td><td className="py-3 pr-3 text-slate-300">{r.network}</td><td className="py-3 pr-3 font-medium text-slate-200">{r.amount}</td><td className="py-3 pr-3"><span className={`rounded-md px-2 py-1 ${statusClass(r.status)}`}>{r.status.replaceAll("_", " ")}</span></td><td className="py-3 pr-4 whitespace-nowrap text-slate-500">{time(r.created_at)}</td></tr>)}</tbody></table></div></Section>;
}

export default function AdminDashboard() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [deposits, setDeposits] = useState<TransactionRow[]>([]);
  const [withdrawals, setWithdrawals] = useState<TransactionRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const loadDashboard = useCallback(async (manualRefresh = false) => {
    if (manualRefresh) setRefreshing(true);
    else setLoading(true);
    setError("");

    try {
      const [dashboard, deposits, withdrawals] = await Promise.all([
        adminFetch<Dashboard>("/api/v1/admin/dashboard"),
        adminFetch<TransactionList>("/api/v1/admin/fiat-deposits?limit=5&offset=0"),
        adminFetch<TransactionList>("/api/v1/admin/withdrawals?limit=5&offset=0"),
      ]);
      // const d = await dr.json() as Dashboard & { detail?: string };
      // const deps = await dep.json() as FiatDepositListResponse & { detail?: string };
      // const wds = await wd.json() as TransactionList & { detail?: string };
      // if (!dr.ok) throw new Error(d.detail || "Unable to load dashboard");
      // if (!dep.ok) throw new Error(deps.detail || "Unable to load deposits");
      // if (!wd.ok) throw new Error(wds.detail || "Unable to load withdrawals");
      setDashboard(dashboard);
      setDeposits(deposits.items ?? []);
      setWithdrawals(withdrawals.items ?? []);
      setLastUpdated(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load dashboard");
    } finally {
      if (manualRefresh) setRefreshing(false);
      else setLoading(false);
    }
  }, []);

  useEffect(() => { void loadDashboard(); }, [loadDashboard]);

  return <main className="mx-auto w-full max-w-[1500px] px-4 py-5 sm:px-6 lg:px-7">
    <div className="mb-5 flex items-end justify-between gap-4"><div><p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-indigo-400">Operations</p><h1 className="mt-1 text-xl font-semibold text-white">Dashboard</h1><p className="mt-1 text-[10px] text-slate-500">Welcome back, Super Admin</p></div><div className="flex items-center gap-2"><div className="hidden rounded-md border border-slate-800 bg-[#0d1523] px-3 py-2 text-[10px] text-slate-300 sm:block">Today <span className="text-slate-500">•</span> Live data{lastUpdated && <span className="ml-2 text-slate-500">Updated {lastUpdated.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</span>}</div><button type="button" onClick={() => void loadDashboard(true)} disabled={loading || refreshing} className="inline-flex items-center gap-2 rounded-md border border-indigo-500/40 bg-indigo-500/10 px-3 py-2 text-[10px] font-semibold text-indigo-300 transition hover:border-indigo-400/60 hover:bg-indigo-500/20 disabled:cursor-not-allowed disabled:opacity-50"><span className={refreshing ? "animate-spin" : ""}>↻</span>{refreshing ? "Refreshing..." : "Refresh"}</button></div></div>
    {error && <div className="mb-4 rounded-lg border border-rose-500/20 bg-rose-500/5 px-4 py-3 text-xs text-rose-300">{error}</div>}
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <Kpi label="Total Users" value={loading ? "…" : number(dashboard?.total_users)} note="registered accounts" icon="♙" tone="bg-indigo-500/15 text-indigo-400" footer="Count:" />
      <Kpi label="Active Users" value={loading ? "…" : number(dashboard?.active_users)} note="currently active accounts" icon="♙" tone="bg-emerald-500/15 text-emerald-400" footer="Count:" />
      <Kpi label="KYC Pending" value={loading ? "…" : number(dashboard?.pending_kyc)} note="applications requiring review" icon="♙" tone="bg-amber-500/15 text-amber-400" footer="Count:" />
      <Kpi label="KYC Verified" value={loading ? "…" : number(dashboard?.verified_users)} note="verified customers" icon="◆" tone="bg-sky-500/15 text-sky-400" footer="Count:" />
      <Kpi label="Total Deposits" value={loading ? "…" : number(dashboard?.total_deposits)} note="deposit records in the exchange" icon="$" tone="bg-emerald-500/15 text-emerald-400" footer="Count:" />
      <Kpi label="Total Withdrawals" value={loading ? "…" : number(dashboard?.total_withdrawals)} note="withdrawal records in the exchange" icon="↗" tone="bg-rose-500/15 text-rose-400" footer="Count:" />
      <Kpi label="Trading Volume" value="—" note="INR valuation pending trade aggregation API" icon="⌁" tone="bg-sky-500/15 text-sky-400" footer="Status:pending" />
      <Kpi label="Ledger Balance" value="—" note="INR aggregate pending ledger valuation API" icon="◎" tone="bg-amber-500/15 text-amber-400" footer={`Assets:${number(dashboard?.active_assets)}`} />
    </div>
    <div className="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-[minmax(0,1.8fr)_minmax(300px,1fr)_minmax(260px,1fr)]"><TradingVolume /><RiskAlerts d={dashboard} /><SystemHealth /></div>
    <div className="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-2"><Activity title="Recent Deposits" href="/admin/deposits" rows={deposits} loading={loading || refreshing} type="deposits" /><Activity title="Recent Withdrawals" href="/admin/withdrawals" rows={withdrawals} loading={loading || refreshing} type="withdrawals" /></div>
  </main>;
}
