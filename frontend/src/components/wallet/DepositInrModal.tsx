"use client";

import { useState } from "react";
import { X, ShieldCheck, Landmark } from "lucide-react";
import { getAccessToken } from "@/lib/api";
import { getCashfree } from "@/lib/cashfree";
import { getPaymentHistory } from "@/lib/paymentApi";
// import { createPaymentOrder } from "@/lib/paymentApi";

interface Props {
  open: boolean;
  onClose: () => void;
  onPaymentSuccess: () => Promise<void>;
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

export default function DepositInrModal({ open, onClose, onPaymentSuccess }: Props) {
  const [amount, setAmount] = useState(500);
  const [loading, setLoading] = useState(false);
  const isValidAmount = amount >= 100 && amount <= 200000;
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isCheckingPayment, setIsCheckingPayment] = useState(false);

  if (!open) return null;

  async function waitForPaymentSuccess(orderId: string) {
    setIsCheckingPayment(true);

    const maxAttempts = 24;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      console.log(`Polling attempt ${attempt}`, orderId);

      try {
        // Fetch fresh payment history every poll.
        const { items } = await getPaymentHistory();

        const payment = items.find(
          (item) => item.gateway_order_id === orderId
        );

        console.log("Matched payment:", {
          orderId: payment?.gateway_order_id,
          status: payment?.status,
          gatewayPaymentId: payment?.gateway_payment_id,
        });

        if (!payment) {
          await new Promise((r) => setTimeout(r, 5000));
          continue;
        }

        if (payment.status === "SUCCESS") {
          console.log("Payment SUCCESS");

          window.dispatchEvent(new Event("order-created"));

          await onPaymentSuccess();

          setIsCheckingPayment(false);
          onClose();
          return;
        }

        if (payment.status === "FAILED") {
          throw new Error("Payment failed.");
        }

        if (payment.status === "CANCELLED") {
          throw new Error("Payment cancelled.");
        }
      } catch (err) {
        console.error("Polling error:", err);
      }

      await new Promise((r) => setTimeout(r, 5000));
    }

    setIsCheckingPayment(false);
    setError("Payment confirmation timed out.");
  }

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
        redirectTarget: "_modal",
    });

    console.log("Checkout result:", result);
    console.log("After checkout");
    // Phase 7.3
    // Cashfree checkout will open here.
    

    // Order creation is finished.
    setLoading(false);

    // Wait for the Cashfree modal to close.
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Start polling for webhook confirmation
    await waitForPaymentSuccess(order.gateway_order_id);

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
            disabled={!isValidAmount || loading || isCheckingPayment}
            className={`w-full rounded-xl py-3 font-medium text-white transition ${
                isValidAmount
                    ? "bg-emerald-600 hover:bg-emerald-500"
                    : "cursor-not-allowed bg-slate-700 text-slate-400"
            }`}
        >
            {loading
                ? "Creating Order..."
                : isCheckingPayment
                  ? "Waiting for payment confirmation..."
                  : `Continue with ₹${amount.toLocaleString("en-IN")}`}
        </button>
        </div>
      </div>
    </div>
  );
}