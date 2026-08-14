interface WalletSummaryProps {
  totalValue: string;
  available: string;
  locked: string;
  cryptoValue?: string;
}

export default function WalletSummary({
  totalValue,
  available,
  locked,
  cryptoValue = "₹ 7,11,000",
}: WalletSummaryProps) {
  return (
    <section className="rounded-xl border border-gray-800 bg-[#11161c] p-5 text-white">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Wallet Overview</h2>

        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm">
          View Wallet
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <div className="rounded-lg bg-gray-900 p-4">
          <p className="text-sm text-gray-400">Total Wallet Value</p>
          <h3 className="mt-2 text-2xl font-bold">{totalValue}</h3>
        </div>

        <div className="rounded-lg bg-gray-900 p-4">
          <p className="text-sm text-gray-400">Available INR</p>
          <h3 className="mt-2 text-xl font-semibold">{available}</h3>
        </div>

        <div className="rounded-lg bg-gray-900 p-4">
          <p className="text-sm text-gray-400">Locked Balance</p>
          <h3 className="mt-2 text-xl font-semibold">{locked}</h3>
        </div>

        <div className="rounded-lg bg-gray-900 p-4">
          <p className="text-sm text-gray-400">Crypto Value</p>
          <h3 className="mt-2 text-xl font-semibold">{cryptoValue}</h3>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <button className="rounded-lg border border-gray-700 px-5 py-2">
          Deposit
        </button>
        <button className="rounded-lg border border-gray-700 px-5 py-2">
          Withdraw
        </button>
        <button className="rounded-lg border border-gray-700 px-5 py-2">
          Transfer
        </button>
      </div>
    </section>
  );
}
