"use client";

const stats = [
  { title: "24h Change", value: "+2.45%", sub: "+₹18,250.00", tone: "text-green-400" },
  { title: "Active Assets", value: "12 Coins", sub: "+2 from last month", tone: "text-white" },
  { title: "Trading Status", value: "Active", sub: "All systems operational", tone: "text-blue-400" },
];

export default function DashboardStats() {
  return (
    <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
      {stats.map((item) => (
        <div key={item.title} className="rounded-xl border border-white/10 bg-[#111827] p-5">
          <p className="text-sm text-gray-400">{item.title}</p>
          <p className={`mt-2 text-2xl font-bold ${item.tone}`}>{item.value}</p>
          <p className="mt-1 text-xs text-gray-400">{item.sub}</p>
        </div>
      ))}
    </section>
  );
}
