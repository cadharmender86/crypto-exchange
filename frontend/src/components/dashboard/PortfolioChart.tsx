"use client";

export default function PortfolioChart() {
  return (
    <section className="rounded-xl border border-white/10 bg-[#111318] p-6 text-white">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Portfolio Performance</h2>
        <div className="flex gap-2 text-xs text-gray-400">
          <span>1D</span>
          <span>7D</span>
          <span>30D</span>
          <span>1Y</span>
        </div>
      </div>

      <div className="mt-6 flex h-40 items-end gap-3">
        {[35, 45, 40, 65, 55, 80, 90].map((value, index) => (
          <div
            key={index}
            className="flex-1 rounded-t bg-blue-500/70"
            style={{ height: `${value}%` }}
          />
        ))}
      </div>

      <p className="mt-4 text-sm text-gray-400">
        Portfolio value trend based on wallet and trading activity.
      </p>
    </section>
  );
}
