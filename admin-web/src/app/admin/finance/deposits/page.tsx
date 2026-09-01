"use client";

import FinanceDepositManagement from "@/components/admin/FinanceDepositManagement";

export default function FinanceDepositsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Fiat Deposits</h1>
        <p className="text-slate-400">
          Review, approve and reject INR deposit requests.
        </p>
      </div>

      <FinanceDepositManagement />
    </div>
  );
}