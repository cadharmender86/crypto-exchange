"use client";

const menuItems = [
  "Dashboard",
  "Easy Buy / Sell",
  "Trade",
  "Futures",
  "Invest",
  "Earn",
  "Wallet",
  "Orders",
  "History",
  "Settings",
  "Support",
  "More",
];

export default function Sidebar() {
  return (
    <aside className="hidden lg:flex w-64 min-h-screen flex-col border-r border-gray-800 bg-[#0b0e11] p-5 text-white">
      <div className="mb-8 text-2xl font-bold text-blue-400">BitNova</div>
      <nav className="space-y-2">
        {menuItems.map((item, index) => (
          <div key={item} className={`rounded-lg px-4 py-3 text-sm ${index === 0 ? "bg-blue-600/20 text-blue-400" : "text-gray-300 hover:bg-gray-800"}`}>
            {item}
          </div>
        ))}
      </nav>
    </aside>
  );
}
