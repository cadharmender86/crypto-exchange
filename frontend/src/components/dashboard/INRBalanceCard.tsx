"use client";

type INRBalanceCardProps = {
  availableBalance?: number;
  lockedBalance?: number;
  openOrders?: number;
  showBalance?: boolean;
};

export default function INRBalanceCard({
  availableBalance = 0,
  lockedBalance = 0,
  openOrders = 0,
  showBalance = true,
}: INRBalanceCardProps) {
  const totalBalance = availableBalance + lockedBalance;

  const maskedBalance = "••••••";

  return (
    <section className="h-full rounded-lg border border-white/[0.06] bg-[#10161d] p-4 text-white">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-sm font-bold">INR Balance</h2>
      </div>

      <div className="space-y-2 text-[10px]">
        {/* Available Balance */}
        <div>
          <p className="text-slate-400">Available Balance</p>
          <p className="mt-0.5 text-base font-bold">
            {showBalance
              ? `₹ ${availableBalance.toLocaleString("en-IN")}`
              : `₹ ${maskedBalance}`}
          </p>
        </div>

        {/* Locked Balance */}
        <div>
          <p className="text-slate-400">Locked Balance</p>
          <p className="mt-0.5 text-base font-bold">
            {showBalance
              ? `₹ ${lockedBalance.toLocaleString("en-IN")}`
              : `₹ ${maskedBalance}`}
          </p>
        </div>

        {/* Open Orders - remains visible */}
        <div>
          <p className="text-slate-400">Open Orders</p>
          <p className="mt-0.5 text-base font-bold">
            {openOrders}
          </p>
        </div>
      </div>

      <div className="my-3 border-t border-white/[0.08]" />

      {/* Total Balance */}
      <p className="text-[10px] text-slate-400">
        Total INR Balance
      </p>

      <p className="mt-1 text-base font-bold">
        {showBalance
          ? `₹ ${totalBalance.toLocaleString("en-IN")}`
          : `₹ ${maskedBalance}`}
      </p>

      <div className="mt-4 flex gap-2">
        <button className="rounded-md bg-blue-600 px-4 py-2 text-xs font-semibold shadow-lg shadow-blue-600/15">
          Deposit
        </button>

        <button className="rounded-md border border-white/15 px-4 py-2 text-xs font-semibold">
          Withdraw
        </button>

        <button className="rounded-md border border-white/15 px-3 py-2 text-xs font-semibold">
          History
        </button>
      </div>
    </section>
  );
}