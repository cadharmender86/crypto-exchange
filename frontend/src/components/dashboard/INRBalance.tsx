"use client";

export default function INRBalance() {
  return (
    <section className="rounded-xl border border-white/10 bg-[#111827] p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-semibold text-white">INR Balance</h2>
        <span className="text-xs text-gray-400">Wallet</span>
      </div>

      <p className="text-sm text-gray-400">Available Balance</p>
      <p className="mt-2 text-2xl font-bold text-white">₹0.00</p>

      <div className="mt-5 grid grid-cols-2 gap-3">
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white">
          Deposit
        </button>
        <button className="rounded-lg border border-white/20 px-4 py-2 text-sm text-white">
          Withdraw
        </button>
      </div>

      <div className="mt-5 space-y-2 text-sm text-gray-400">
        <div className="flex justify-between">
          <span>Locked Balance</span>
          <span>₹0.00</span>
        </div>
        <div className="flex justify-between">
          <span>Open Orders</span>
          <span>0</span>
        </div>
      </div>
    </section>
  );
}
