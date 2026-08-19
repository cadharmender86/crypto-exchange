"use client";

import Link from "next/link";
import { useState } from "react";

export default function DashboardHeader() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-30 h-[54px] border-b border-white/[0.06] bg-[#080d12]/95 px-4 backdrop-blur-xl md:px-6 lg:px-5">
      <div className="flex h-full items-center justify-between">
        <div className="flex items-center gap-4">
          <button className="text-lg text-slate-400 transition hover:text-white lg:hidden" aria-label="Open menu">☰</button>
          <div className="flex items-center gap-2.5 lg:hidden">
            <span className="text-2xl font-black text-blue-400">N</span>
            <span className="text-lg font-bold">BitNova</span>
          </div>
        </div>

        <div className="ml-auto flex items-center gap-3 md:gap-5">
          <button className="rounded-lg bg-gradient-to-r from-blue-600 to-blue-500 px-5 py-2 text-sm font-bold shadow-lg shadow-blue-600/20 transition hover:brightness-110 md:px-6">Deposit</button>
          <button className="relative text-lg text-slate-300 transition hover:text-white" aria-label="Notifications">
            ♧<span className="absolute -right-1 -top-1 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-red-500 text-[8px] font-bold text-white">2</span>
          </button>
          <div className="relative">
            <button onClick={() => setMenuOpen((v) => !v)} className="flex items-center gap-2" aria-expanded={menuOpen}>
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#252a31] text-xs font-bold text-slate-200 ring-1 ring-white/10">DK</span>
              <span className="text-xs text-slate-400">⌄</span>
            </button>
            {menuOpen && (
              <div className="absolute right-0 top-10 w-36 rounded-lg border border-white/10 bg-[#11161d] p-2 text-xs shadow-2xl">
                <Link href="/profile" onClick={() => setMenuOpen(false)} className="block w-full rounded px-3 py-2 text-left hover:bg-white/5">Profile</Link>
                <button className="w-full rounded px-3 py-2 text-left hover:bg-white/5">Logout</button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
