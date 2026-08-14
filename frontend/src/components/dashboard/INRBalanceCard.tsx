"use client";

type INRBalanceCardProps = {
  availableBalance?: number;
  lockedBalance?: number;
  openOrders?: number;
};

export default function INRBalanceCard({
  availableBalance = 0,
  lockedBalance = 0,
  openOrders = 0,
}: INRBalanceCardProps) {
  const totalBalance = availableBalance + lockedBalance;

  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-6">
      <h2 className="mb-5 text-lg font-semibold text-white">
        INR Balance
      </h2>

      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-400">Available Balance</p>
          <h3 className="mt-1 text-2xl font-bold text-white">
            ₹ {availableBalance.toLocaleString("en-IN")}
          </h3>
        </div>

        <div>
          <p className="text-sm text-gray-400">Locked Balance</p>
          <h3 className="mt-1 text-xl font-semibold text-white">
            ₹ {lockedBalance.toLocaleString("en-IN")}
          </h3>
        </div>

        <div>
          <p className="text-sm text-gray-400">Open Orders</p>
          <h3 className="mt-1 text-xl font-semibold text-white">
            {openOrders}
          </h3>
        </div>

        <div className="border-t border-gray-800 pt-4">
          <p className="text-sm text-gray-400">Total INR Balance</p>
          <h3 className="mt-1 text-2xl font-bold text-white">
            ₹ {totalBalance.toLocaleString("en-IN")}
          </h3>
        </div>

        <div className="mt-5 flex gap-3">
          <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white">
            Deposit
          </button>

          <button className="rounded-lg border border-gray-700 px-4 py-2 text-sm font-medium text-white">
            Withdraw
          </button>

          <button className="rounded-lg border border-gray-700 px-4 py-2 text-sm font-medium text-white">
            History
          </button>
        </div>
      </div>
    </section>
  );
}
