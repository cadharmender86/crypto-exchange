"use client";

export default function DashboardHeader() {
  return (
    <>
      <header className="mb-5 flex items-center justify-between rounded-xl border border-white/10 bg-[#0b0f15] px-6 py-4">
        <div>
          <h1 className="text-xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-gray-400">Welcome back to BitNova 👋</p>
        </div>

        <div className="flex items-center gap-4">
          <button className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold">
            Deposit
          </button>
          <div className="relative text-xl">🔔</div>
          <div className="rounded-full bg-gray-800 px-3 py-2 text-sm">DK</div>
          <span className="text-gray-400">⌄</span>
        </div>
      </header>

      <section className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-white/10 bg-[#111722] p-5">
          <p className="text-sm text-gray-400">24h Change</p>
          <p className="mt-2 text-xl font-bold text-green-400">+2.45%</p>
          <p className="text-xs text-green-400">+₹18,250</p>
        </div>

        <div className="rounded-xl border border-white/10 bg-[#111722] p-5">
          <p className="text-sm text-gray-400">Active Assets</p>
          <p className="mt-2 text-xl font-bold">12 Coins</p>
          <p className="text-xs text-green-400">+2 from last month</p>
        </div>

        <div className="rounded-xl border border-white/10 bg-[#111722] p-5">
          <p className="text-sm text-gray-400">Trading Status</p>
          <p className="mt-2 text-xl font-bold text-blue-400">Active</p>
          <p className="text-xs text-green-400">All systems operational</p>
        </div>
      </section>
    </>
  );
}
