interface WalletSummaryProps {
  totalValue: string;
  available: string;
  locked: string;
}

export default function WalletSummary({
  totalValue,
  available,
  locked,
}: WalletSummaryProps) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
        <p className="text-sm text-gray-400">Total Wallet Value</p>
        <h2 className="mt-2 text-2xl font-bold">{totalValue}</h2>
      </div>

      <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
        <p className="text-sm text-gray-400">Available Balance</p>
        <h2 className="mt-2 text-2xl font-bold">{available}</h2>
      </div>

      <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
        <p className="text-sm text-gray-400">Locked Balance</p>
        <h2 className="mt-2 text-2xl font-bold">{locked}</h2>
      </div>
    </div>
  );
}
