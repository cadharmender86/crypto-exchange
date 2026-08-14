"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
  Account,
  Asset,
  getAccessToken,
  getAccounts,
  getAssets,
  getDeposits,
  Deposit,
} from "@/lib/api";

const formatAmount = (value: string | number) =>
  new Intl.NumberFormat("en-IN", { maximumFractionDigits: 4 }).format(Number(value));

export default function WalletPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [deposits, setDeposits] = useState<Deposit[]>([]);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      window.location.href = "/login";
      return;
    }

    Promise.all([getAccounts(token), getAssets(), getDeposits(token)]).then(
      ([accountData, assetData, depositData]) => {
        setAccounts(accountData);
        setAssets(assetData);
        setDeposits(depositData);
      },
    );
  }, []);

  const assetMap = useMemo(
    () => new Map(assets.map((asset) => [asset.id, asset])),
    [assets],
  );

  return (
    <main className="min-h-screen bg-[#070b14] px-6 py-8 text-white">
      <div className="mx-auto max-w-7xl">
        <Link href="/dashboard" className="text-blue-400">← Dashboard</Link>

        <h1 className="mt-6 text-3xl font-bold">Wallet</h1>
        <p className="text-gray-400">Manage your crypto assets</p>

        <section className="mt-8 grid gap-5 md:grid-cols-3">
          {accounts.map((account) => {
            const asset = assetMap.get(account.asset_id);
            const symbol = asset?.symbol ?? account.asset_id;

            return (
              <div key={account.id} className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <h2 className="text-xl font-bold">{symbol}</h2>
                <p className="mt-3 text-gray-400">Available</p>
                <p className="text-2xl font-bold">{formatAmount(account.available_balance)}</p>

                <div className="mt-5 flex gap-3">
                  <Link
                    href={`/wallet/deposit?asset=${symbol}`}
                    className="rounded-lg bg-blue-600 px-4 py-2 text-sm"
                  >
                    Deposit
                  </Link>
                  <Link
                    href={`/wallet/withdraw?asset=${symbol}`}
                    className="rounded-lg border border-white/20 px-4 py-2 text-sm"
                  >
                    Withdraw
                  </Link>
                </div>
              </div>
            );
          })}
        </section>

        <section className="mt-8 rounded-2xl border border-white/10 bg-white/5 p-6">
          <h2 className="text-xl font-semibold">Recent Wallet Activity</h2>
          {deposits.slice(0, 5).map((deposit) => (
            <div key={deposit.id} className="mt-4 rounded-lg bg-black/20 p-3">
              Deposit {formatAmount(deposit.amount)} {assetMap.get(deposit.asset_id)?.symbol}
            </div>
          ))}
        </section>
      </div>
    </main>
  );
}
