"use client";

type INRBalanceCardProps = {
  availableBalance?: number;
  lockedBalance?: number;
  openOrders?: number;
};

export default function INRBalanceCard({
  availableBalance = 50000,
  lockedBalance = 10000,
  openOrders = 0,
}: INRBalanceCardProps) {
  const totalBalance = availableBalance + lockedBalance;

  return (
    <section className="rounded-2xl border border-white/10 bg-[#111318] p-5 text-white">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-lg font-semibold">INR Balance</h2>
        <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs text-blue-400">INR</span>
      </div>

      <div>
        <p className="text-sm text-gray-400">Available Balance</p>
        <p className="mt-1 text-3xl font-bold">₹ {availableBalance.toLocaleString("en-IN")}</p>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-4">
        <div className="rounded-xl bg-black/20 p-3">
          <p className="text-xs text-gray-400">Locked</p>
          <p className="mt-1 font-semibold">₹ {lockedBalance.toLocaleString("en-IN")}</p>
        </div>
        <div className="rounded-xl bg-black/20 p-3">
          <p className="text-xs text-gray-400">Open Orders</p>
          <p className="mt-1 font-semibold">{openOrders}</p>
        </div>
      </div>

      <div className="mt-5 rounded-xl border border-white/10 p-3">
        <p className="text-xs text-gray-400">Total INR Balance</p>
        <p className="mt-1 text-xl font-bold">₹ {totalBalance.toLocaleString("en-IN")}</p>
      </div>

      <div className="mt-5 flex gap-3">
        <button className="flex-1 rounded-lg bg-blue-600 py-2 text-sm font-medium">Deposit</button>
        <button className="flex-1 rounded-lg border border-white/20 py-2 text-sm font-medium">Withdraw</button>
      </div>
    </section>
  );
}
