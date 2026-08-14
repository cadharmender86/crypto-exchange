"use client";

export default function DashboardHeader() {
  return (
    <section className="mb-6 rounded-xl border border-gray-800 bg-[#111318] p-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold text-white">
          Dashboard
        </h1>
        <p className="text-sm text-gray-400">
          Welcome back to BitNova
        </p>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-lg bg-gray-900 p-4">
          <p className="text-sm text-gray-400">24h Change</p>
          <h3 className="mt-2 text-xl font-bold text-green-400">
            +2.45%
          </h3>
        </div>

        <div className="rounded-lg bg-gray-900 p-4">
          <p className="text-sm text-gray-400">Active Assets</p>
          <h3 className="mt-2 text-xl font-bold text-white">
            12 Coins
          </h3>
        </div>

        <div className="rounded-lg bg-gray-900 p-4">
          <p className="text-sm text-gray-400">Trading Status</p>
          <h3 className="mt-2 text-xl font-bold text-blue-400">
            Active
          </h3>
        </div>
      </div>
    </section>
  );
}
