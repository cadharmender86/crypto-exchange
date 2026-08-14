"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Account, Deposit, getAccounts, getAccessToken, getDeposits, getWallets, Wallet, logout } from "@/lib/api";

export default function DashboardPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [deposits, setDeposits] = useState<Deposit[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      window.location.href = "/login";
      return;
    }

    Promise.all([getAccounts(token), getWallets(token), getDeposits(token)])
      .then(([accountData, walletData, depositData]) => {
        setAccounts(accountData);
        setWallets(walletData);
        setDeposits(depositData);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  const total = accounts.reduce((sum, account) => sum + Number(account.total_balance), 0);

  return (
    <main className="min-h-screen bg-[#070b14] px-4 py-8 text-white lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <Link href="/" className="text-sm text-blue-400">← BitNova</Link>
            <h1 className="mt-2 text-3xl font-bold">Dashboard</h1>
          </div>
          <button onClick={() => { logout(); window.location.href = "/"; }} className="rounded-lg border border-white/10 px-4 py-2 text-sm text-gray-300 hover:bg-white/5">
            Logout
          </button>
        </div>

        {error && <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">{error}</div>}

        <section className="mt-8 grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <p className="text-sm text-gray-400">Total balance</p>
            <p className="mt-2 text-3xl font-bold">{total.toFixed(4)}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <p className="text-sm text-gray-400">Wallets</p>
            <p className="mt-2 text-3xl font-bold">{wallets.length}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <p className="text-sm text-gray-400">Deposits</p>
            <p className="mt-2 text-3xl font-bold">{deposits.length}</p>
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <h2 className="text-xl font-semibold">Accounts</h2>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-white/10 text-gray-400">
                <tr><th className="px-3 py-3">Asset ID</th><th className="px-3 py-3">Available</th><th className="px-3 py-3">Locked</th><th className="px-3 py-3">Total</th><th className="px-3 py-3">Status</th></tr>
              </thead>
              <tbody>
                {accounts.map((account) => (
                  <tr key={account.id} className="border-b border-white/5">
                    <td className="px-3 py-3 font-mono text-xs">{account.asset_id}</td>
                    <td className="px-3 py-3">{account.available_balance}</td>
                    <td className="px-3 py-3">{account.locked_balance}</td>
                    <td className="px-3 py-3 font-semibold">{account.total_balance}</td>
                    <td className="px-3 py-3">{account.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!accounts.length && <p className="py-6 text-gray-500">No accounts returned by the API.</p>}
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <h2 className="text-xl font-semibold">Recent deposits</h2>
          <div className="mt-4 space-y-3">
            {deposits.slice(0, 10).map((deposit) => (
              <div key={deposit.id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/5 bg-black/20 p-4">
                <div><p className="font-semibold">{deposit.amount} · {deposit.network}</p><p className="mt-1 font-mono text-xs text-gray-500">{deposit.blockchain_tx_hash}</p></div>
                <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-gray-300">{deposit.status}</span>
              </div>
            ))}
            {!deposits.length && <p className="py-6 text-gray-500">No deposits returned by the API.</p>}
          </div>
        </section>
      </div>
    </main>
  );
}
