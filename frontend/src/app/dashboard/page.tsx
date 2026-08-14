"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  Account,
  Asset,
  Deposit,
  getAccounts,
  getAccessToken,
  getAssets,
  getDeposits,
  getWallets,
  Wallet,
  logout,
} from "@/lib/api";

function formatAmount(value: string | number, maximumFractionDigits = 4) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return String(value);
  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits,
  }).format(amount);
}

function shortHash(value: string) {
  if (!value || value.length <= 20) return value;
  return `${value.slice(0, 10)}...${value.slice(-8)}`;
}

export default function DashboardPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [deposits, setDeposits] = useState<Deposit[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      window.location.href = "/login";
      return;
    }

    Promise.all([
      getAccounts(token),
      getAssets(),
      getWallets(token),
      getDeposits(token),
    ])
      .then(([accountData, assetData, walletData, depositData]) => {
        setAccounts(accountData);
        setAssets(assetData);
        setWallets(walletData);
        setDeposits(depositData);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  const assetMap = useMemo(
    () => new Map(assets.map((asset) => [asset.id, asset])),
    [assets],
  );

  const total = accounts.reduce(
    (sum, account) => sum + Number(account.total_balance),
    0,
  );

  return (
    <main className="min-h-screen bg-[#070b14] px-4 py-6 text-white lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-5">
          <div className="flex flex-wrap items-center gap-6">
            <Link href="/" className="text-xl font-bold text-white">
              BitNova
            </Link>
            <nav className="flex flex-wrap gap-4 text-sm text-gray-400">
              <Link href="/dashboard" className="text-white">Dashboard</Link>
              <Link href="/markets" className="hover:text-white">Markets</Link>
              <Link href="/buy-sell" className="hover:text-white">Buy / Sell</Link>
              <Link href="/otc" className="hover:text-white">OTC</Link>
              <Link href="/fees" className="hover:text-white">Fees</Link>
            </nav>
          </div>
          <button
            onClick={() => {
              logout();
              window.location.href = "/";
            }}
            className="rounded-lg border border-white/10 px-4 py-2 text-sm text-gray-300 hover:bg-white/5"
          >
            Logout
          </button>
        </header>

        <div className="mt-8">
          <p className="text-sm text-blue-400">Account overview</p>
          <h1 className="mt-1 text-3xl font-bold">Dashboard</h1>
        </div>

        {error && (
          <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
            {error}
          </div>
        )}

        <section className="mt-8 grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <p className="text-sm text-gray-400">Total balance</p>
            <p className="mt-2 text-3xl font-bold">{formatAmount(total)}</p>
            <p className="mt-1 text-xs text-gray-500">Across all asset accounts</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <p className="text-sm text-gray-400">Wallets</p>
            <p className="mt-2 text-3xl font-bold">{wallets.length}</p>
            <p className="mt-1 text-xs text-gray-500">Active exchange wallets</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <p className="text-sm text-gray-400">Deposits</p>
            <p className="mt-2 text-3xl font-bold">{deposits.length}</p>
            <p className="mt-1 text-xs text-gray-500">Recent deposit records</p>
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-xl font-semibold">Accounts</h2>
            <Link href="/markets" className="text-sm text-blue-400 hover:text-blue-300">
              View markets →
            </Link>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-white/10 text-gray-400">
                <tr>
                  <th className="px-3 py-3">Asset</th>
                  <th className="px-3 py-3">Available</th>
                  <th className="px-3 py-3">Locked</th>
                  <th className="px-3 py-3">Total</th>
                  <th className="px-3 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {accounts.map((account) => {
                  const asset = assetMap.get(account.asset_id);
                  const symbol = asset?.symbol ?? account.asset_id;
                  return (
                    <tr key={account.id} className="border-b border-white/5">
                      <td className="px-3 py-4">
                        <div className="font-semibold">{symbol}</div>
                        {asset?.name && (
                          <div className="mt-1 text-xs text-gray-500">{asset.name}</div>
                        )}
                      </td>
                      <td className="px-3 py-4">{formatAmount(account.available_balance)}</td>
                      <td className="px-3 py-4">{formatAmount(account.locked_balance)}</td>
                      <td className="px-3 py-4 font-semibold">{formatAmount(account.total_balance)}</td>
                      <td className="px-3 py-4">
                        <span className="rounded-full bg-green-500/10 px-3 py-1 text-xs text-green-300">
                          {account.status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {!accounts.length && !error && (
              <p className="py-6 text-gray-500">No accounts returned by the API.</p>
            )}
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-xl font-semibold">Recent deposits</h2>
            <span className="text-xs text-gray-500">Latest 10</span>
          </div>

          <div className="mt-4 space-y-3">
            {deposits.slice(0, 10).map((deposit) => {
              const asset = assetMap.get(deposit.asset_id);
              const symbol = asset?.symbol ?? deposit.network;
              return (
                <div
                  key={deposit.id}
                  className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-white/5 bg-black/20 p-4"
                >
                  <div className="min-w-0">
                    <p className="font-semibold">
                      {formatAmount(deposit.amount)} {symbol}
                    </p>
                    <p className="mt-1 text-xs text-gray-500">
                      Network: {deposit.network}
                    </p>
                    <p className="mt-1 font-mono text-xs text-gray-600">
                      TX: {shortHash(deposit.blockchain_tx_hash)}
                    </p>
                  </div>
                  <span className="rounded-full bg-yellow-500/10 px-3 py-1 text-xs uppercase text-yellow-300">
                    {deposit.status}
                  </span>
                </div>
              );
            })}
            {!deposits.length && !error && (
              <p className="py-6 text-gray-500">No deposits returned by the API.</p>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
