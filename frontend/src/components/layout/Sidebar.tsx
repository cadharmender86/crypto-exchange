"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const menuItems = [
  { name: "Dashboard", icon: "▣", href: "/dashboard" },
  { name: "Easy Buy / Sell", icon: "⊕", href: "/buy-sell" },
  { name: "Trade", icon: "⌁", href: "/trade" },
  { name: "Futures", icon: "◉", href: "/futures" },
  { name: "Invest", icon: "♧", href: "/invest" },
  { name: "Earn", icon: "✧", href: "/earn" },
  { name: "Wallet", icon: "▤", href: "/wallet" },
  { name: "Orders", icon: "▱", href: "/orders" },
  { name: "History", icon: "◷", href: "/history" },
  { name: "Refer & Earn", icon: "♧", href: "/refer" },
  { name: "Settings", icon: "⚙", href: "/settings" },
  { name: "Support", icon: "?", href: "/support" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-[240px] flex-col border-r border-white/[0.07] bg-[#080d12] text-white">
      <div className="flex h-[54px] items-center gap-2.5 border-b border-white/[0.05] px-4">
        <span className="text-[28px] font-black leading-none tracking-[-4px] text-blue-500">
          N
        </span>
        <span className="text-[17px] font-bold tracking-tight">BitNova</span>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-5">
        {menuItems.map((item) => {
          const active =
            pathname === item.href ||
            (item.href !== "/dashboard" &&
              pathname.startsWith(`${item.href}/`));

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-base font-medium transition ${
                active
                  ? "border border-blue-500/10 bg-[#102443] text-blue-400 shadow-[0_5px_20px_rgba(0,95,255,.08)]"
                  : "text-slate-300 hover:bg-white/[0.04] hover:text-white"
              }`}
            >
              <span className="w-4 shrink-0 text-center text-sm text-slate-300">
                {item.icon}
              </span>

              <span className="truncate">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mx-3 mb-4 rounded-lg border border-white/[0.06] bg-[#0d141c] p-3 shadow-[0_8px_24px_rgba(0,0,0,.18)]">
        <p className="text-xs font-bold">BitNova App</p>
        <p className="mt-2 text-[11px] text-slate-300">Trade on the go</p>
        <p className="text-[11px] text-slate-300">Anytime, Anywhere</p>

        <div className="mt-3 grid grid-cols-2 gap-1">
          <div className="h-16 rounded-md border border-white/10 bg-gradient-to-b from-slate-700/80 via-slate-900 to-black" />
          <div className="h-16 rounded-md border border-white/10 bg-gradient-to-b from-slate-700/80 via-slate-900 to-black" />
        </div>

        <div className="mt-2 grid grid-cols-2 gap-1 text-[7px]">
          <span className="rounded bg-black px-1 py-1 text-center">
             App Store
          </span>
          <span className="rounded bg-black px-1 py-1 text-center">
            ▶ Play
          </span>
        </div>
      </div>

      <div className="px-3 pb-4">
        <div className="flex rounded-lg bg-[#101820] p-1 text-[11px]">
          <button className="flex-1 rounded-md py-2 text-slate-400">
            Light
          </button>

          <button className="flex-1 rounded-md bg-blue-600 py-2 font-semibold text-white shadow">
            Dark
          </button>
        </div>
      </div>

      <div className="border-t border-white/[0.06] px-4 py-4 text-[11px] leading-5 text-slate-400">
        © 2025 BitNova
        <br />
        All rights reserved
      </div>
    </aside>
  );
}