"use client";

import { useEffect, useState } from "react";
import { X, AlertTriangle } from "lucide-react";
import { createWithdrawal } from "@/services/withdrawal.service";
import { randomUUID } from "crypto";

type WithdrawModalProps = {
  open: boolean;
  asset: {
    account_id: string;
    asset_id: string;
    symbol: string;
    name: string;
    available_balance: string;
    is_fiat: boolean;
  } | null;
  onClose: () => void;
  onWithdrawalSuccess: () => Promise<void>;
};

export default function WithdrawModal({
  open,
  asset,
  onClose,
  onWithdrawalSuccess,
}: WithdrawModalProps) {
  const [network, setNetwork] = useState("");
  const [address, setAddress] = useState("");
  const [amount, setAmount] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open || !asset) return;

    setNetwork(asset.symbol === "USDT" ? "SEPOLIA" : "");
    setAddress("");
    setAmount("");
    setError("");
  }, [open, asset]);

  if (!open || !asset) return null;

  const available = Number(asset.available_balance);
  const withdrawAmount = Number(amount || "0");


  const isValid =
    address.trim().length > 0 &&
    network !== "" &&
    !Number.isNaN(withdrawAmount) &&
    withdrawAmount > 0 &&
    withdrawAmount <= available;

  console.log({
  address,
  amount,
  available: asset.available_balance,
  withdrawAmount: Number(amount || "0"),
  isValid,
});  

  const handleWithdraw = async () => {
    if (!isValid || !asset) {
      setError("Please enter a valid address and amount.");
      return;
    }

    try {
        setLoading(true);
        setError("");

        await createWithdrawal ({
            asset_id: asset.asset_id,
            network,
            destination_address: address.trim(),
            amount,
            // idempotency_key: crypto.randomUUID(),
        });

        // Refresh wallet balances and transactions.
        await onWithdrawalSuccess();

        onClose();
    } catch (err: any) {
        setError(
            err?.message ||
            "Unable to submit withdrawal request."
        );
    } finally {
        setLoading(false);
    }
};
    

    // Phase 8.6.2
    // console.log("Withdraw Request", {
    //   asset: asset.symbol,
    //   network,
    //   address,
    //   amount,
    // });

    // onClose();


  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div className="w-full max-w-lg rounded-2xl border border-white/10 bg-[#111827] p-6 shadow-2xl">

        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">
              Withdraw {asset.symbol}
            </h2>

            <p className="text-sm text-gray-400">{asset.name}</p>
          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-2 text-gray-400 hover:bg-white/10 hover:text-white"
          >
            <X size={20} />
          </button>
        </div>

        {/* Available */}
        <div className="mb-5 rounded-xl bg-zinc-900 p-4">
          <p className="text-xs uppercase text-gray-500">
            Available Balance
          </p>

          <p className="mt-2 text-2xl font-semibold text-white">
            {available.toFixed(asset.is_fiat ? 2 : 6)} {asset.symbol}
          </p>
        </div>

        {/* Network */}
        <div className="mb-4">
          <label className="mb-2 block text-sm text-gray-400">
            Network
          </label>

          <select
            value={network}
            onChange={(e) => setNetwork(e.target.value)}
            className="w-full rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-white"
          >
            <option value="SEPOLIA">SEPOLIA</option>
          </select>
        </div>

        {/* Address */}
        <div className="mb-4">
          <label className="mb-2 block text-sm text-gray-400">
            Destination Address
          </label>

          <textarea
            rows={3}
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="Paste recipient wallet address"
            className="w-full rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-white"
          />
        </div>

        {/* Amount */}
        <div className="mb-5">
          <label className="mb-2 block text-sm text-gray-400">
            Amount
          </label>

          <input
            type="number"
            min="0"
            step="0.000001"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder={`0 ${asset.symbol}`}
            className="w-full rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-white"
          />

          <button
            onClick={() => setAmount(asset.available_balance)}
            className="mt-2 text-sm text-green-400 hover:text-green-300"
          >
            Withdraw Max
          </button>
        </div>

        {/* Summary */}
        <div className="mb-5 rounded-xl border border-zinc-800 bg-zinc-900 p-4 text-sm">
          <div className="flex justify-between py-1">
            <span className="text-gray-400">Amount</span>
            <span className="text-white">
              {withdrawAmount || 0} {asset.symbol}
            </span>
          </div>

          <div className="flex justify-between py-1">
            <span className="text-gray-400">Network Fee</span>
            <span className="text-white">0.000000 {asset.symbol}</span>
          </div>

          <div className="mt-3 flex justify-between border-t border-zinc-700 pt-3 font-semibold">
            <span className="text-white">You Receive</span>
            <span className="text-green-400">
              {withdrawAmount || 0} {asset.symbol}
            </span>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-700 bg-red-900/20 p-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {/* Warning */}
        <div className="mb-5 rounded-lg border border-yellow-600 bg-yellow-900/20 p-4 text-sm text-yellow-300">
          <div className="mb-2 flex items-center gap-2 font-semibold">
            <AlertTriangle size={18} />
            Important
          </div>

          <ul className="list-disc space-y-1 pl-5">
            <li>Withdraw only to a {network} address.</li>
            <li>Blockchain withdrawals cannot be reversed.</li>
            <li>Double-check the destination address before submitting.</li>
          </ul>
        </div>

        {/* Submit */}
        <button
          type="button"
          onClick={handleWithdraw}
          disabled={!isValid || loading}
          className={`w-full rounded-lg py-3 font-semibold transition-colors ${
            !isValid || loading
              ? "cursor-not-allowed bg-zinc-700 text-zinc-400"
              : "bg-red-600 text-white hover:bg-red-500"
          }`}
        >
          {loading ? "Submitting..." : "Submit Withdrawal"}
        </button>

      </div>
    </div>
  );
}