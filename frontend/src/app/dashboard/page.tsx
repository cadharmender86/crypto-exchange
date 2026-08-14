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

const formatAmount = (value: string | number) =>
  new Intl.NumberFormat("en-IN", { maximumFractionDigits: 4 }).format(Number(value));

export default function DashboardPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [deposits, setDeposits] = useState<Deposit[]>([]);

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
    ]).then(([a, assets, w, d]) => {
      setAccounts(a);
      setAssets(assets);
      setWallets(w);
      setDeposits(d);
    });
  }, []);

  const assetMap = useMemo(
    () => new Map(assets.map((asset) => [asset.id, asset])),
    [assets]
  );

  const portfolioValue = accounts.reduce(
    (sum, item) => sum + Number(item.total_balance),
    0
  );

  return (
    <main className="min-h-screen bg-[#070b14] px-6 py-8 text-white">
      <div className="mx-auto max-w-7xl">
        <header className="flex justify-between border-b border-white/10 pb-5">
          <nav className="flex gap-6">
            <Link href="/dashboard" className="font-bold text-xl">BitNova</Link>
            <Link href="/markets">Markets</Link>
            <Link href="/buy-sell">Easy Buy/Sell</Link>
            <Link href="/otc">OTC</Link>
          </nav>
          <button onClick={() => { logout(); window.location.href = "/"; }}>
            Logout
          </button>
        </header>

        <h1 className="mt-8 text-3xl font-bold">Portfolio Overview</h1>
        <p className="text-gray-400">Manage your crypto assets and activity</p>

        <section className="mt-8 grid gap-5 md:grid-cols-5">
          {[
            ["Total Portfolio Value", `₹ ${formatAmount(portfolioValue)}`],
            ["INR Balance", "₹ 0"],
            ["Crypto Holdings", `${accounts.length} Assets`],
            ["Profit / Loss", "+0.00%"],
            ["30 Days Volume", "Coming soon"],
          ].map(([title, value]) => (
            <div key={title} className="rounded-2xl border border-white/10 bg-white/5 p-5">
              <p className="text-sm text-gray-400">{title}</p>
              <p className="mt-3 text-xl font-bold">{value}</p>
            </div>
          ))}
        </section>

        <section className="mt-8 rounded-2xl border border-white/10 bg-white/5 p-6">
          <h2 className="text-xl font-semibold">Quick Actions</h2>
          <p className="mt-2 text-sm text-gray-400">Manage each crypto asset directly</p>

          <div className="mt-5 space-y-3">
            {accounts.map((account) => {
              const asset = assetMap.get(account.asset_id);
              const symbol = asset?.symbol || account.asset_id;

              return (
                <div key={account.id} className="flex flex-wrap items-center justify-between gap-4 rounded-xl bg-black/20 p-4">
                  <div>
                    <p className="font-semibold">{symbol}</p>
                    <p className="text-sm text-gray-400">Balance: {formatAmount(account.total_balance)}</p>
                  </div>

                  <div className="flex gap-3">
                    <Link className="rounded-lg bg-blue-600 px-5 py-2" href={`/wallet/deposit?asset=${symbol}`}>
                      Deposit
                    </Link>
                    <Link className="rounded-lg border border-white/20 px-5 py-2" href={`/wallet/withdraw?asset=${symbol}`}>
                      Withdraw
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-white/10 bg-white/5 p-6">
          <h2 className="text-xl font-semibold">Coin Balance</h2>
          {accounts.map((account) => (
            <div key={account.id} className="mt-3 grid grid-cols-4 rounded-xl bg-black/20 p-4">
              <span>{assetMap.get(account.asset_id)?.symbol || account.asset_id}</span>
              <span>{formatAmount(account.available_balance)}</span>
              <span>{formatAmount(account.locked_balance)}</span>
              <span>{formatAmount(account.total_balance)}</span>
            </div>
          ))}
        </section>

        <section className="mt-8 grid gap-6 md:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
            <h2 className="text-xl font-semibold">Open Orders</h2>
            <p className="mt-4 text-gray-400">Trading orders will appear after order-book implementation.</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
            <h2 className="text-xl font-semibold">Trade History</h2>
            <p className="mt-4 text-gray-400">Completed trades will appear here.</p>
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-white/10 bg-white/5 p-6">
          <h2 className="text-xl font-semibold">Transaction History</h2>
          {deposits.slice(0, 5).map((deposit) => (
            <div key={deposit.id} className="mt-3 rounded-lg bg-black/20 p-3">
              Deposit {formatAmount(deposit.amount)} {assetMap.get(deposit.asset_id)?.symbol}
            </div>
          ))}
        </section>
      </div>
    </main>
  );
}
