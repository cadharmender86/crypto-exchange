"use client";

import { useState } from "react";
import { X, ShieldCheck, Landmark } from "lucide-react";
import { getAccessToken } from "@/lib/api";
import { getCashfree } from "@/lib/cashfree";
// import { createPaymentOrder } from "@/lib/paymentApi";

interface Props {
  open: boolean;
  onClose: () => void;
}

const createPaymentOrder = async (amount: number) => {
  const token = getAccessToken();

  const response = await fetch("http://localhost:8000/api/v1/payments/orders", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      amount,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Unable to create payment order");
  }

  return data;
};

export default function DepositInrModal({ open, onClose }: Props) {
  const [amount, setAmount] = useState(500);
  const [loading, setLoading] = useState(false);
  const isValidAmount = amount >= 100 && amount <= 200000;
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);

  if (!open) return null;

  async function handleContinue() {
  setError("");
  setSessionId(null);

  if (!isValidAmount) {
    setError("Deposit amount must be between ₹100 and ₹2,00,000.");
    return;
  }

  try {
    setLoading(true);

    const order = await createPaymentOrder(amount);
    console.log("Order:", order);

    const cashfree = await getCashfree();
    console.log("Cashfree:", cashfree);

    if (!cashfree) {
        throw new Error("Cashfree SDK not loaded");
    }

    console.log("Before checkout");

    const result = await cashfree.checkout({
        paymentSessionId: order.payment_session_id,
        redirectTarget: "_self",
    });

    console.log("Checkout result:", result);
    console.log("After checkout");
    // Phase 7.3
    // Cashfree checkout will open here.
} catch (err: any) {
    console.error(err);

    setError(
      err?.response?.data?.detail ||
      err?.message ||
      "Unable to create payment order."
    );
  } finally {
    setLoading(false);
  }
}

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div className="w-full max-w-md rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-700 px-6 py-4">
          <div>
            <h2 className="text-lg font-semibold text-white">
              Deposit INR
            </h2>

            <p className="text-xs text-slate-400">
              Add funds instantly using UPI, Cards or Net Banking.
            </p>
          </div>

          <button onClick={onClose}>
            <X className="h-5 w-5 text-slate-400 hover:text-white" />
          </button>
        </div>

        <div className="space-y-5 p-6">
          <div>
            <label className="text-sm text-slate-400">
              Deposit Amount (INR)
            </label>

            <input
              type="text"
              inputMode="numeric"
              maxLength={6}
              placeholder="Enter amount"
              value={amount === 0 ? "" : amount}
              onChange={(e) => {
                const digitsOnly = e.target.value.replace(/\D/g, "");

                if(!digitsOnly) {
                  setAmount(0);
                  return;
                }

                const value = Math.min(Number(digitsOnly), 200000);
                setAmount(value);
              }}
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-lg text-white outline-none focus:border-emerald-500"
            />

            <p className="mt-2 text-xs text-slate-500">
              Min ₹100 • Max ₹2,00,000
            </p>
          </div>

          <div className="rounded-xl border border-slate-700 bg-slate-800 p-4">
            <div className="flex items-center gap-3">
              <Landmark className="h-6 w-6 text-emerald-400" />

              <div>
                <div className="font-medium text-white">
                  Cashfree Payments
                </div>

                <div className="text-xs text-slate-400">
                  UPI • Credit Card • Debit Card • Net Banking
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-emerald-900 bg-emerald-950/40 p-4">
            <div className="flex gap-3">
              <ShieldCheck className="mt-0.5 h-5 w-5 text-emerald-400" />

              <p className="text-xs text-slate-300">
                Payments are processed securely through Cashfree Payment Gateway.
                BitNova never stores your card details.
              </p>
            </div>
          </div>

          {error && (
            <div className="rounded-lg bg-red-950 p-3 text-sm text-red-300">
              {error}
            </div>
          )}

          {sessionId && (
            <div className="rounded-lg bg-blue-950 p-3 text-xs text-blue-300">
              Payment order created successfully.
              <br />
              Session ID received from backend.
            </div>
          )}

        <button
            onClick={handleContinue}
            disabled={!isValidAmount || loading}
            className={`w-full rounded-xl py-3 font-medium text-white transition ${
                isValidAmount
                    ? "bg-emerald-600 hover:bg-emerald-500"
                    : "cursor-not-allowed bg-slate-700 text-slate-400"
            }`}
        >
            {loading
                ? "Creating Order..."
                : `Continue with ₹${amount.toLocaleString("en-IN")}`}
        </button>
        </div>
      </div>
    </div>
  );
}