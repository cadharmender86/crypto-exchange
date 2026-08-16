"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { clearAdminSession, getAdminMe, type AdminSession } from "@/lib/adminApi";

type NavItem = {
  href: string;
  label: string;
  icon: string;
  permission: string;
  superAdminOnly?: boolean;
};

type NavGroup = {
  label: string;
  items: NavItem[];
};

const navGroups: NavGroup[] = [
  { label: "ADMINISTRATION", items: [
    { href: "/admin", label: "Dashboard", icon: "⌂", permission: "USER_READ" },
    { href: "/admin/administrators", label: "Administrators", icon: "♙", permission: "ADMIN_MANAGE", superAdminOnly: true },
    { href: "/admin/rbac", label: "RBAC Management", icon: "◈", permission: "ADMIN_MANAGE", superAdminOnly: true },
    { href: "/admin/kyc", label: "KYC Management", icon: "▣", permission: "KYC_READ" },
    { href: "/admin/users", label: "User Management", icon: "♙", permission: "USER_READ" },
    { href: "/admin/support", label: "Support Management", icon: "◌", permission: "USER_READ" },
  ] },
  { label: "FINANCE", items: [
    { href: "/admin/wallets", label: "Wallets", icon: "▣", permission: "WALLET_READ" },
    { href: "/admin/deposits", label: "Deposits", icon: "⇩", permission: "DEPOSIT_READ" },
    { href: "/admin/withdrawals", label: "Withdrawals", icon: "⇧", permission: "WITHDRAWAL_READ" },
    { href: "/admin/transactions", label: "Transactions", icon: "▤", permission: "LEDGER_READ" },
  ] },
  { label: "TRADING", items: [
    { href: "/admin/markets", label: "Markets", icon: "◫", permission: "ORDER_READ" },
    { href: "/admin/orders", label: "Orders", icon: "☷", permission: "ORDER_READ" },
    { href: "/admin/trades", label: "Trades", icon: "⇄", permission: "ORDER_READ" },
    { href: "/admin/trading", label: "Trading Operations", icon: "⌁", permission: "ORDER_READ" },
  ] },
  { label: "COMPLIANCE & RISK", items: [
    { href: "/admin/compliance", label: "Compliance", icon: "◇", permission: "KYC_READ" },
    { href: "/admin/risk", label: "Risk Management", icon: "△", permission: "KYC_READ" },
    { href: "/admin/suspicious-activity", label: "Suspicious Activity", icon: "!", permission: "KYC_READ" },
  ] },
  { label: "SYSTEM", items: [
    { href: "/admin/audit", label: "Audit Logs", icon: "◷", permission: "AUDIT_READ" },
    { href: "/admin/notifications", label: "Notifications", icon: "♧", permission: "USER_READ" },
    { href: "/admin/settings", label: "System Settings", icon: "⚙", permission: "ADMIN_MANAGE", superAdminOnly: true },
  ] },
  { label: "REPORTS", items: [
    { href: "/admin/reports/activity", label: "Activity Reports", icon: "▥", permission: "AUDIT_READ" },
    { href: "/admin/reports/access", label: "Access Reports", icon: "▥", permission: "AUDIT_READ" },
    { href: "/admin/reports/financial", label: "Financial Reports", icon: "▤", permission: "LEDGER_READ" },
    { href: "/admin/reports/trading", label: "Trading Reports", icon: "◫", permission: "ORDER_READ" },
  ] },
];

export default function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [session, setSession] = useState<AdminSession | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (pathname === "/admin/login") { setCheckingAuth(false); return; }
    getAdminMe().then(setSession).catch(() => router.replace("/admin/login")).finally(() => setCheckingAuth(false));
  }, [pathname, router]);

  const logout = () => { clearAdminSession(); router.replace("/admin/login"); };
  if (pathname === "/admin/login") return <>{children}</>;
  if (checkingAuth || !session) return <div className="flex min-h-screen items-center justify-center bg-[#020b1c] text-sm text-slate-400">Checking admin session…</div>;

  const isSuperAdmin = session.roles.includes("SUPER_ADMIN");
  const visibleGroups = navGroups.map((group) => ({ ...group, items: group.items.filter((item) => session.permissions.includes(item.permission) && (!item.superAdminOnly || isSuperAdmin)) })).filter((group) => group.items.length > 0);
  const flatNav = visibleGroups.flatMap((group) => group.items);
  const initials = (session.full_name || session.email || "A").charAt(0).toUpperCase();
  const adminLabel = isSuperAdmin ? "Super Admin" : "Administrator";
  const isActive = (href: string) => href === "/admin" ? pathname === "/admin" : pathname === href || pathname.startsWith(`${href}/`);

  return (
    <div className="min-h-screen bg-[#020b1c] text-slate-100 lg:flex">
      <aside className="hidden h-screen w-[278px] shrink-0 border-r border-slate-800/80 bg-[#031027] lg:sticky lg:top-0 lg:flex lg:flex-col">
        <div className="flex h-[72px] shrink-0 items-center gap-3 border-b border-slate-800/80 px-7">
          <div className="text-[37px] font-black leading-none text-blue-600">B</div>
          <div className="text-[22px] font-bold tracking-tight text-slate-100">BitNova</div>
        </div>
        <nav className="min-h-0 flex-1 overflow-y-auto px-4 py-6">
          {visibleGroups.map((group) => <div key={group.label} className="mb-6 last:mb-2">
            <div className="px-3 pb-2 text-[11px] font-medium tracking-wide text-slate-500">{group.label}</div>
            <div className="space-y-1">{group.items.map((item) => <Link key={`${item.label}-${item.href}`} href={item.href} className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] font-medium transition ${isActive(item.href) ? "bg-blue-600 text-white shadow-lg shadow-blue-950/30" : "text-slate-300 hover:bg-slate-800/50 hover:text-white"}`}><span className="grid w-5 place-items-center text-[16px] opacity-90">{item.icon}</span><span className="truncate">{item.label}</span></Link>)}</div>
          </div>)}
        </nav>
        <div className="shrink-0 border-t border-slate-800/80 p-4"><div className="flex items-center gap-3 px-1 py-2">
          <div className="relative"><div className="grid h-10 w-10 place-items-center rounded-full bg-indigo-500 text-sm font-semibold text-white">{initials}</div><span className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-[#031027] bg-emerald-400" /></div>
          <div className="min-w-0 flex-1"><div className="truncate text-sm font-semibold text-white">{adminLabel}</div><div className="truncate text-[11px] text-slate-400">{session.email}</div></div>
          <button onClick={logout} aria-label="Logout" className="text-slate-400 hover:text-white">⌄</button>
        </div></div>
      </aside>
      <main className="min-w-0 flex-1">
        <header className="sticky top-0 z-20 flex h-[72px] items-center justify-between border-b border-slate-800/80 bg-[#020b1c]/95 px-4 backdrop-blur lg:px-7">
          <div className="flex min-w-0 items-center gap-4"><button className="grid h-9 w-9 place-items-center rounded-lg border border-slate-800 bg-[#07142a] text-slate-300 lg:hidden">☰</button><div className="hidden text-sm text-slate-400 sm:block">Admin / <span className="text-slate-200">{flatNav.find((item) => isActive(item.href))?.label || "Dashboard"}</span></div><div className="relative hidden md:block"><span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">⌕</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search anything..." className="h-10 w-72 rounded-full border border-slate-700 bg-[#07142a] pl-9 pr-4 text-xs text-slate-200 outline-none placeholder:text-slate-500 focus:border-blue-500/70" /></div></div>
          <div className="flex items-center gap-3"><button className="relative grid h-9 w-9 place-items-center text-xl text-slate-300" aria-label="Notifications">♧<span className="absolute right-0.5 top-0.5 h-2 w-2 rounded-full bg-rose-500" /></button><button className="grid h-9 w-9 place-items-center text-lg text-slate-300" aria-label="Theme">◐</button><button onClick={logout} className="grid h-9 w-9 place-items-center text-lg text-slate-300" aria-label="Logout">↪</button></div>
        </header>
        <div className="border-b border-slate-800/80 bg-[#031027] px-3 py-2 lg:hidden"><div className="flex gap-2 overflow-x-auto">{flatNav.map((item) => <Link key={`mobile-${item.label}`} href={item.href} className={`whitespace-nowrap rounded-lg border px-3 py-1.5 text-xs ${isActive(item.href) ? "border-blue-500/60 bg-blue-600 text-white" : "border-slate-700 text-slate-300"}`}>{item.label}</Link>)}</div></div>
        <section className="p-4 sm:p-5 lg:p-7 xl:p-8">{children}</section>
      </main>
    </div>
  );
}
