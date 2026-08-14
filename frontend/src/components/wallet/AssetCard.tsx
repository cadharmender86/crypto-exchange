interface AssetCardProps {
  symbol: string;
  name?: string;
  balance: string;
  value?: string;
  onDeposit?: () => void;
  onWithdraw?: () => void;
}

export default function AssetCard({
  symbol,
  name,
  balance,
  value,
  onDeposit,
  onWithdraw,
}: AssetCardProps) {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-5">
      <div className="flex justify-between">
        <div>
          <h3 className="text-lg font-semibold">{symbol}</h3>
          <p className="text-sm text-gray-400">{name || symbol}</p>
        </div>
        <div className="text-right">
          <p className="font-medium">{balance}</p>
          {value && <p className="text-sm text-gray-400">{value}</p>}
        </div>
      </div>

      <div className="mt-4 flex gap-3">
        <button onClick={onDeposit} className="rounded-lg bg-blue-600 px-4 py-2 text-sm">
          Deposit
        </button>
        <button onClick={onWithdraw} className="rounded-lg border border-gray-700 px-4 py-2 text-sm">
          Withdraw
        </button>
      </div>
    </div>
  );
}
