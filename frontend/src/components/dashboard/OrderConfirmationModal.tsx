"use client";

interface Props {
  open: boolean;
  coin: string;
  mode: "BUY" | "SELL";
  payAmount: number;
  receiveAmount: string;
  fee: number;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function OrderConfirmationModal({
  open,
  coin,
  mode,
  payAmount,
  receiveAmount,
  fee,
  onConfirm,
  onCancel,
}: Props) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
      <div className="w-full max-w-md rounded-2xl border border-gray-800 bg-[#111318] p-6 text-white">
        <h3 className="text-xl font-semibold">Confirm Order</h3>

        <div className="mt-5 space-y-3 text-sm text-gray-300">
          <div className="flex justify-between"><span>Pair</span><span>{coin}/INR</span></div>
          <div className="flex justify-between"><span>Side</span><span className={mode === "BUY" ? "font-semibold text-emerald-400" : "font-semibold text-red-400"}>{mode}</span></div>
          <div className="flex justify-between"><span>You Pay</span><span>₹{payAmount}</span></div>
          <div className="flex justify-between"><span>You Receive</span><span>{receiveAmount} {coin}</span></div>
          <div className="flex justify-between"><span>Fee</span><span>₹{fee.toFixed(2)}</span></div>
        </div>

        <div className="mt-6 flex gap-3">
          <button onClick={onCancel} className="flex-1 rounded-xl border border-gray-700 py-3">Cancel</button>
          <button onClick={onConfirm} className={`flex-1 rounded-xl py-3 font-semibold text-white ${mode === "BUY" ? "bg-emerald-600 hover:bg-emerald-500" : "bg-red-600 hover:bg-red-500"}`}>Confirm {mode}</button>
        </div>
      </div>
    </div>
  );
}
