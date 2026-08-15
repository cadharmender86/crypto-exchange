"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const nav = [
  { href: "/admin", label: "Dashboard", icon: "▦" },
  { href: "/admin/users", label: "Users", icon: "◉" },
  { href: "/admin/kyc", label: "KYC", icon: "✓" },
  { href: "/admin/deposits", label: "Deposits", icon: "↓" },
  { href: "/admin/withdrawals", label: "Withdrawals", icon: "↑" },
  { href: "/admin/orders", label: "Orders", icon: "⇄" },
  { href: "/admin/ledger", label: "Ledger", icon: "▤" },
  { href: "/admin/audit", label: "Audit Log", icon: "◷" },
  { href: "/admin/settings", label: "Settings", icon: "⚙" },
];

export default function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-[#080d18] text-slate-100 lg:flex">
      <aside className="hidden w-64 shrink-0 border-r border-slate-800 bg-[#0b111e] lg:flex lg:flex-col">
        <div className="flex h-20 items-center border-b border-slate-800 px-6">
          <div>
            <div className="text-lg font-bold tracking-tight">BitNova</div>
            <div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-cyan-400">Admin Console</div>
          </div>
        </div>
        <nav className="flex-1 space-y-1 p-4">
          {nav.map((item) => {
            const active = item.href === "/admin" ? pathname === "/admin" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium ${
                  active ? "bg-cyan-500/10 text-cyan-300 ring-1 ring-cyan-500/20" : "text-slate-400 hover:bg-slate-800/70 hover:text-white"
                }`}
              >
                <span className="w-5 text-center text-base">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-slate-800 p-4">
          <div className="rounded-xl bg-slate-900/70 p-3">
            <div className="text-xs text-slate-500">Signed in as</div>
            <div className="mt-1 text-sm font-semibold">Super Admin</div>
            <div className="mt-1 text-xs text-cyan-400">RBAC enabled</div>
          </div>
        </div>
      </aside>

      <main className="min-w-0 flex-1">
        <header className="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-slate-800/90 bg-[#080d18]/95 px-5 backdrop-blur lg:px-8">
          <div>
            <div className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Operations</div>
            <h1 className="mt-1 text-xl font-semibold">{nav.find((item) => item.href !== "/admin" && pathname.startsWith(item.href))?.label ?? "Dashboard"}</h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-300 sm:block">● Systems operational</div>
            <Link href="/admin/login" className="rounded-lg border border-slate-700 px-3 py-2 text-xs font-semibold text-slate-300 hover:border-slate-500 hover:text-white">Logout</Link>
          </div>
        </header>
        <div className="border-b border-slate-800 bg-[#0b111e] px-4 py-2 lg:hidden">
          <div className="flex gap-2 overflow-x-auto pb-1">
            {nav.map((item) => (
              <Link key={item.href} href={item.href} className="whitespace-nowrap rounded-lg border border-slate-700 px-3 py-2 text-xs font-medium text-slate-300">
                {item.label}
              </Link>
            ))}
          </div>
        </div>
        <section className="p-5 lg:p-8">{children}</section>
      </main>
    </div>
  );
}
