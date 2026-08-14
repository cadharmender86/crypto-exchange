"use client";

const items = [
  { name: "Home", icon: "⌂" },
  { name: "Trade", icon: "⌁" },
  { name: "Wallet", icon: "▤" },
  { name: "Orders", icon: "▱" },
  { name: "Profile", icon: "◯" },
];

export default function MobileBottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 flex border-t border-white/10 bg-[#070b10] px-2 py-2 text-white lg:hidden">
      {items.map((item, index) => (
        <button
          key={item.name}
          className={`flex flex-1 flex-col items-center gap-1 rounded-lg py-2 text-xs ${
            index === 0 ? "bg-blue-600/20 text-blue-400" : "text-gray-400"
          }`}
        >
          <span className="text-lg">{item.icon}</span>
          {item.name}
        </button>
      ))}
    </nav>
  );
}
