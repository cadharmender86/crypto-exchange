"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ArrowDownLeft,
  ArrowUpRight,
  Search,
  Wallet,
  RefreshCw,
} from "lucide-react";

import {
  DashboardWalletBalance,
  getWalletDashboard,
  getWalletTransactions,
  WalletBalance,
} from "@/services/wallet.service";

import DepositModal from "@/components/wallet/DepositModal";
import DepositInrModal from "@/components/wallet/DepositInrModal";
import WithdrawModal from "@/components/wallet/WithdrawModal";


interface WalletTransaction {
  id: string;
  reference: string;
  transaction_type: string;
  status: string;
  description: string;
  created_at: string;
}

export default function WalletPage() {
  const [balances, setBalances] = useState<DashboardWalletBalance[]>([]);
  const [transactions, setTransactions] = useState<WalletTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [hideZero, setHideZero] = useState(false);
  const [depositAsset, setDepositAsset] = useState<DashboardWalletBalance | null>(null);
  const [withdrawAsset, setWithdrawAsset] = useState<DashboardWalletBalance | null>(null);
  const [showInrDeposit, setShowInrDeposit] = useState(false);

  async function loadWallet() {
    setLoading(true);

    try {
      const dashboard = await getWalletDashboard();
      const history = await getWalletTransactions();

      setBalances(dashboard.balances);
      setTransactions(history);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadWallet();
  }, []);

  const filteredBalances = useMemo(() => {
    return balances.filter((asset) => {
      const total =
        Number(asset.available_balance) +
        Number(asset.locked_balance);

      const matches =
        asset.symbol.toLowerCase().includes(search.toLowerCase()) ||
        asset.name.toLowerCase().includes(search.toLowerCase());

      if (hideZero && total === 0) return false;

      return matches;
    });
  }, [balances, search, hideZero]);

  const totalPortfolio = useMemo(() => {
    return balances
      .filter((a) => a.is_fiat)
      .reduce((sum, a) => sum + Number(a.available_balance), 0);
  }, [balances]);

  return (
    <main className="min-h-screen bg-black text-white p-6">
      <div className="mx-auto max-w-7xl space-y-8">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold">My Wallet</h1>
            <p className="text-zinc-400 mt-1">
              Unified Ledger Wallet — BitNova Exchange
            </p>
          </div>

          <button
            onClick={loadWallet}
            className="flex items-center gap-2 rounded-lg border border-zinc-700 px-4 py-2 hover:bg-zinc-900"
          >
            <RefreshCw size={18} />
            Refresh
          </button>
        </div>

        {/* Portfolio Summary */}
        <section className="rounded-2xl bg-gradient-to-r from-emerald-600 to-cyan-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <Wallet size={30} />
            <h2 className="text-2xl font-semibold">Portfolio Value</h2>
          </div>

          <p className="text-5xl font-bold">
            ₹ {totalPortfolio.toLocaleString("en-IN")}
          </p>

          <p className="mt-2 text-emerald-100">
            Customer available INR balance
          </p>
        </section>

        {/* Search + Toggle */}
        <div className="flex flex-col md:flex-row gap-4 justify-between">

          <div className="relative w-full md:w-96">
            <Search
              className="absolute left-3 top-3 text-zinc-500"
              size={18}
            />

            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search asset..."
              className="w-full rounded-xl bg-zinc-900 border border-zinc-700 pl-10 pr-4 py-3 outline-none"
            />
          </div>

          <label className="flex items-center gap-3 text-zinc-300">
            <input
              type="checkbox"
              checked={hideZero}
              onChange={(e) => setHideZero(e.target.checked)}
            />

            Hide zero balances
          </label>
        </div>

        {/* Balance Cards */}
        <section className="grid md:grid-cols-2 xl:grid-cols-3 gap-5">
          {filteredBalances.map((asset) => (
            <div
              key={asset.account_id}
              className="rounded-2xl border border-zinc-800 bg-zinc-950 p-5"
            >
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-xl font-semibold">{asset.symbol}</h3>
                  <p className="text-zinc-500">{asset.name}</p>
                </div>

                <span
                  className={`rounded-full px-3 py-1 text-xs ${
                    asset.is_fiat
                      ? "bg-green-500/20 text-green-300"
                      : "bg-cyan-500/20 text-cyan-300"
                  }`}
                >
                  {asset.is_fiat ? "FIAT" : "CRYPTO"}
                </span>
              </div>

              <div className="mt-6 space-y-2 text-sm">

                <div className="flex justify-between">
                  <span className="text-zinc-400">Available</span>
                  <span>{Number(asset.available_balance).toFixed(asset.is_fiat ? 2 : 6)}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-zinc-400">Locked</span>
                  <span>{Number(asset.locked_balance).toFixed(asset.is_fiat ? 2 : 6)}</span>
                </div>

                <div className="flex justify-between border-t border-zinc-800 pt-3 text-base font-semibold">
                  <span>Total</span>

                  <span>
                    {(
                      Number(asset.available_balance) +
                      Number(asset.locked_balance)
                    ).toFixed(asset.is_fiat ? 2 : 6)}
                  </span>
                </div>
              </div>

              <div className="mt-6 flex gap-3">

                <button 
                  onClick={() => {
                    if (asset.is_fiat) {
                      setShowInrDeposit(true);
                    } else {
                      setDepositAsset(asset);
                    }
                    }}
                  className="w-full rounded-lg bg-green-600 py-2 font-medium text-white hover:bg-green-500"
                >  
                  Deposit
                </button>

                <button 
                  onClick={() => {
                    if (!asset.is_fiat) {
                      setWithdrawAsset(asset);
                    }
                  }}
                  className="flex-1 rounded-lg border border-zinc-700 py-2 hover:bg-zinc-900">
                  Withdraw
                </button>

              </div>
            </div>
          ))}
        </section>

        {/* Transaction History */}
        <section className="rounded-2xl border border-zinc-800 bg-zinc-950">

          <div className="border-b border-zinc-800 p-5">
            <h2 className="text-2xl font-semibold">
              Recent Transactions
            </h2>
          </div>

          {loading ? (
            <div className="p-8 text-center text-zinc-500">
              Loading transactions...
            </div>
          ) : (
            <div className="divide-y divide-zinc-800">

              {transactions.map((tx) => (
                <div
                  key={tx.id}
                  className="flex items-center justify-between p-5 hover:bg-zinc-900/50"
                >
                  <div className="flex items-center gap-4">

                    {tx.transaction_type.includes("DEPOSIT") ? (
                      <ArrowDownLeft className="text-green-400" />
                    ) : (
                      <ArrowUpRight className="text-orange-400" />
                    )}

                    <div>

                      <div className="font-medium">
                        {tx.transaction_type.replaceAll("_", " ")}
                      </div>

                      <div className="text-sm text-zinc-500">
                        {tx.description}
                      </div>

                      <div className="text-xs text-zinc-600 mt-1">
                        {new Date(tx.created_at).toLocaleString()}
                      </div>

                    </div>

                  </div>

                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      tx.status === "POSTED"
                        ? "bg-green-500/20 text-green-300"
                        : tx.status === "PENDING"
                        ? "bg-yellow-500/20 text-yellow-300"
                        : tx.status === "FAILED"
                        ? "bg-red-500/20 text-red-300"
                        : "bg-zinc-700 text-zinc-300"
                    }`}
                  >
                    {tx.status}
                  </span>

                </div>
              ))}

            </div>
          )}

        </section>

        <DepositModal
          open={depositAsset !== null}
          asset={depositAsset}
          onClose={() => setDepositAsset(null)}
        />

        <WithdrawModal
          open={withdrawAsset != null}
          asset={withdrawAsset}
          onClose={() => setWithdrawAsset(null)}
          onWithdrawalSuccess={loadWallet}
        />   

      </div>
    </main>
  );
}