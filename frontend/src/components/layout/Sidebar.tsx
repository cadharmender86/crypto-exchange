"use client";

import { useState } from "react";

const menuItems = [
  { name: "Dashboard", icon: "▣" },
  { name: "Easy Buy / Sell", icon: "↔" },
  { name: "Trade", icon: "⌁" },
  { name: "Futures", icon: "◉" },
  { name: "Invest", icon: "◈" },
  { name: "Earn", icon: "◎" },
  { name: "Wallet", icon: "▤" },
  { name: "Orders", icon: "▱" },
  { name: "History", icon: "◷" },
  { name: "Refer & Earn", icon: "♧" },
  { name: "Settings", icon: "⚙" },
  { name: "Support", icon: "?" },
  { name: "More", icon: "•••" },
];

export default function Sidebar() {
  const [active, setActive] = useState("Dashboard");

  return (
    <aside className="hidden lg:flex w-64 min-h-screen flex-col border-r border-white/10 bg-[#070b10] text-white">
      <div className="px-5 py-6 text-2xl font-bold tracking-wide">
        <span className="text-blue-500">N</span> BitNova
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {menuItems.map((item) => (
          <button
            key={item.name}
            onClick={() => setActive(item.name)}
            className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-sm transition ${
              active === item.name
                ? "bg-blue-600/20 text-blue-400 border border-blue-500/20"
                : "text-gray-300 hover:bg-white/5"
            }`}
          >
            <span className="w-5 text-center">{item.icon}</span>
            <span>{item.name}</span>
          </button>
        ))}
      </nav>

      <div className="m-4 rounded-xl border border-white/10 bg-[#111722] p-4 text-sm">
        <p className="font-semibold">BitNova App</p>
        <p className="mt-2 text-gray-400">Trade on the go</p>
        <p className="text-gray-400">Anytime, Anywhere</p>
        <button className="mt-3 w-full rounded-lg bg-blue-600 py-2 text-sm">
          Download
        </button>
      </div>

      <div className="flex gap-2 px-4 pb-5">
        <button className="flex-1 rounded-lg border border-white/10 py-2 text-sm text-gray-300">
          Light
        </button>
        <button className="flex-1 rounded-lg bg-blue-600 py-2 text-sm">
          Dark
        </button>
      </div>
    </aside>
  );
}
