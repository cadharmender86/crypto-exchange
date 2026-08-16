"use client";

const stats = [
  { title: "24h Change", value: "+2.45%", sub: "+₹18,250.00", tone: "text-emerald-400", icon: "⌁" },
  { title: "Active Assets", value: "12 Coins", sub: "+2 from last month", tone: "text-white", icon: "◔" },
  { title: "Trading Status", value: "Active", sub: "All systems operational", tone: "text-blue-400", icon: "✓" },
];

export default function DashboardStats() {
  return (
    <section className="grid grid-cols-1 gap-3 md:grid-cols-3">
      {stats.map((item) => (
        <div key={item.title} className="relative min-h-[92px] overflow-hidden rounded-lg border border-white/[0.06] bg-[#10161d] px-4 py-3 shadow-[0_8px_25px_rgba(0,0,0,.12)]">
          <div className="absolute right-3 top-3 flex h-10 w-10 items-center justify-center rounded-full border border-blue-400/20 bg-blue-500/10 text-xl text-blue-400">{item.icon}</div>
          <p className="text-[11px] font-medium text-slate-300">{item.title}</p>
          <p className={`mt-1 text-lg font-bold ${item.tone}`}>{item.value}</p>
          <p className="mt-0.5 text-[10px] font-semibold text-emerald-400">{item.sub}</p>
        </div>
      ))}
    </section>
  );
}
