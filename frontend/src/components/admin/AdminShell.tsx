"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { clearAdminSession, getAdminMe, type AdminSession } from "@/lib/adminApi";

const nav = [
  { href: "/admin", label: "Dashboard", icon: "▦", permission: "USER_READ" },
  { href: "/admin/users", label: "Users", icon: "♙", permission: "USER_READ" },
  { href: "/admin/kyc", label: "KYC Management", icon: "▣", permission: "KYC_READ" },
  { href: "/admin/deposits", label: "Deposits", icon: "◈", permission: "DEPOSIT_READ" },
  { href: "/admin/withdrawals", label: "Withdrawals", icon: "◈", permission: "WITHDRAWAL_READ" },
  { href: "/admin/orders", label: "Orders", icon: "☷", permission: "ORDER_READ" },
  { href: "/admin/orders", label: "Trading", icon: "⌁", permission: "ORDER_READ" },
  { href: "/admin/ledger", label: "Ledger", icon: "▤", permission: "LEDGER_READ" },
  { href: "/admin/audit", label: "Audit Logs", icon: "◷", permission: "AUDIT_READ" },
  { href: "/admin/rbac", label: "RBAC", icon: "♙", permission: "ADMIN_MANAGE", superAdminOnly: true },
  { href: "/admin/settings", label: "Settings", icon: "⚙", permission: "ADMIN_MANAGE", superAdminOnly: true },
];

export default function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [session, setSession] = useState<AdminSession | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (pathname === "/admin/login") {
      setCheckingAuth(false);
      return;
    }

    getAdminMe()
      .then(setSession)
      .catch(() => router.replace("/admin/login"))
      .finally(() => setCheckingAuth(false));
  }, [pathname, router]);

  const logout = () => {
    clearAdminSession();
    router.replace("/admin/login");
  };

  if (pathname === "/admin/login") return <>{children}</>;

  if (checkingAuth || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#070c16] text-sm text-slate-400">
        Checking admin session…
      </div>
    );
  }

  const isSuperAdmin = session.roles.includes("SUPER_ADMIN");
  const visibleNav = nav.filter((item) =>
    session.permissions.includes(item.permission) && (!item.superAdminOnly || isSuperAdmin)
  );
  const initials = (session.full_name || session.email || "A").charAt(0).toUpperCase();
  const adminLabel = isSuperAdmin ? "Super Admin" : "Administrator";

  return (
    <div className="min-h-screen bg-[#070c16] text-slate-100 lg:flex">
      <aside className="hidden w-[222px] shrink-0 border-r border-slate-800/90 bg-[#09101c] lg:flex lg:flex-col">
        <div className="flex h-[62px] items-center gap-3 border-b border-slate-800/90 px-6">
          <div className="grid h-9 w-9 place-items-center rounded-lg bg-amber-400/10 text-lg text-amber-300 ring-1 ring-amber-400/30">⬡</div>
          <div>
            <div className="text-[17px] font-bold tracking-tight text-white">BITNOVA</div>
            <div className="text-[10px] font-semibold tracking-[0.18em] text-slate-400">ADMIN</div>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-5">
          {visibleNav.map((item) => {
            const active = item.href === "/admin"
              ? pathname === "/admin"
              : pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={`${item.label}-${item.href}`}
                href={item.href}
                className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-medium transition ${active ? "bg-indigo-600/90 text-white shadow-lg shadow-indigo-950/40" : "text-slate-400 hover:bg-slate-800/60 hover:text-white"}`}
              >
                <span className="grid w-5 place-items-center text-base opacity-90">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-slate-800/90 p-3">
          <div className="flex items-center gap-3 rounded-xl border border-slate-800 bg-[#0c1422] p-3">
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-slate-700 text-sm font-semibold">{initials}</div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-semibold text-white">{session.full_name || session.email}</div>
              <div className="text-xs text-emerald-400">{adminLabel}</div>
            </div>
            <button onClick={logout} aria-label="Logout" className="text-slate-500 hover:text-white">⌄</button>
          </div>
        </div>
      </aside>

      <main className="min-w-0 flex-1">
        <header className="sticky top-0 z-20 flex h-[62px] items-center justify-between border-b border-slate-800/90 bg-[#070c16]/95 px-4 backdrop-blur lg:px-5">
          <div className="flex min-w-0 items-center gap-3">
            <button className="grid h-9 w-9 place-items-center rounded-lg border border-slate-800 bg-[#0c1422] text-slate-300 hover:text-white lg:hidden">☰</button>
            <div className="relative hidden sm:block">
              <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">⌕</span>
              <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search anything..." className="h-9 w-72 rounded-lg border border-slate-800 bg-[#0c1422] pl-9 pr-16 text-xs text-slate-200 outline-none placeholder:text-slate-600 focus:border-indigo-500/60" />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-slate-600">Ctrl + K</span>
            </div>
          </div>
          <div className="flex items-center gap-2.5">
            <button className="relative grid h-9 w-9 place-items-center rounded-lg border border-slate-800 bg-[#0c1422] text-slate-400 hover:text-white" aria-label="Notifications">♧<span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-rose-500" /></button>
            <button className="grid h-9 w-9 place-items-center rounded-lg border border-slate-800 bg-[#0c1422] text-slate-400 hover:text-white" aria-label="Help">?</button>
            <div className="hidden h-8 w-px bg-slate-800 sm:block" />
            <div className="grid h-9 w-9 place-items-center rounded-full bg-indigo-500/80 text-sm font-semibold">{initials}</div>
            <div className="hidden sm:block">
              <div className="text-xs font-semibold text-white">{session.full_name || "Admin"}</div>
              <div className="text-[10px] text-slate-500">{adminLabel}</div>
            </div>
            <button onClick={logout} className="hidden text-slate-500 hover:text-white sm:block">⌄</button>
          </div>
        </header>

        <div className="border-b border-slate-800/80 bg-[#09101c] px-3 py-2 lg:hidden">
          <div className="flex gap-2 overflow-x-auto">
            {visibleNav.map((item) => {
              const active = item.href === "/admin"
                ? pathname === "/admin"
                : pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link key={`mobile-${item.label}`} href={item.href} className={`whitespace-nowrap rounded-lg border px-3 py-1.5 text-xs ${active ? "border-indigo-500/60 bg-indigo-600/90 text-white" : "border-slate-700 text-slate-300"}`}>
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>

        <section className="p-4 sm:p-5 lg:p-6 xl:p-7">{children}</section>
      </main>
    </div>
  );
}
