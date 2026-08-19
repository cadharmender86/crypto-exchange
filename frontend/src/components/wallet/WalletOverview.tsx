"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import CoinIcon from "@/components/common/CoinIcon";
import { useWallet } from "@/hooks/useWallet";
import { getTransactionHistory, type TransactionHistoryItem } from "@/services/history.service";
import { getMarketAssets, getMarketTicker, type MarketAsset, type MarketTicker } from "@/services/market.service";

function useMarketData() {
  const [assets, setAssets] = useState<MarketAsset[]>([]);
  const [tickers, setTickers] = useState<MarketTicker[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.all([getMarketAssets(), getMarketTicker()])
      .then(([assetData, tickerData]) => {
        if (!active) return;
        setAssets(assetData);
        setTickers(tickerData);
      })
      .catch(() => {
        if (!active) return;
        setAssets([]);
        setTickers([]);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  return { assets, tickers, loading };
}

function formatInr(value: number) {
  return `₹${value.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatBalance(value: number, decimals = 8) {
  return value.toLocaleString("en-IN", { minimumFractionDigits: 0, maximumFractionDigits: decimals });
}

function InrEquivalent({ value }: { value: number }) {
  return <div className="mt-1 text-xs text-slate-500">≈ {formatInr(value)}</div>;
}

function formatTransactionType(value: string) {
  return value.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatTransactionDate(value: string) {
  return new Date(value).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function WalletOverview() {
  const { accounts, loading: walletLoading, error: walletError } = useWallet();
  const { assets, tickers, loading: marketLoading } = useMarketData();
  const [transactions, setTransactions] = useState<TransactionHistoryItem[]>([]);
  const [transactionsLoading, setTransactionsLoading] = useState(true);
  const [transactionsError, setTransactionsError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"ALL" | "CRYPTO" | "FIAT">("ALL");
  const [hideZero, setHideZero] = useState(false);

  useEffect(() => {
    let active = true;
    getTransactionHistory()
      .then((data) => {
        if (active) setTransactions(Array.isArray(data) ? data.slice(0, 10) : []);
      })
      .catch((error) => {
        if (active) {
          setTransactions([]);
          setTransactionsError(error?.message || "Failed to load transaction history");
        }
      })
      .finally(() => {
        if (active) setTransactionsLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const rows = useMemo(() => {
    const assetMap = new Map(assets.map((asset) => [String(asset.id), asset]));
    const tickerMap = new Map(tickers.map((ticker) => [ticker.symbol, ticker]));
    const usdtInr = tickerMap.get("USDTINR")?.price_inr ?? tickerMap.get("USDTINR")?.price ?? 0;

    return accounts.map((account) => {
      const asset = assetMap.get(String(account.asset_id));
      const symbol = asset?.symbol ?? "ASSET";
      const ticker = symbol === "INR" ? undefined : tickerMap.get(`${symbol}INR`) ?? tickerMap.get(`${symbol}USDT`);
      const priceInr = symbol === "INR" ? 1 : ticker?.price_inr ?? (ticker?.price_usdt && usdtInr ? ticker.price_usdt * usdtInr : 0);
      const available = Number(account.available_balance);
      const locked = Number(account.locked_balance);
      const total = Number(account.total_balance);
      const assetType = asset?.asset_type?.toUpperCase() === "FIAT" || symbol === "INR" ? "FIAT" : "CRYPTO";

      return {
        ...account,
        asset,
        symbol,
        name: asset?.name ?? symbol,
        available,
        locked,
        total,
        value: total * priceInr,
        availableValue: available * priceInr,
        lockedValue: locked * priceInr,
        change: ticker?.change_24h ?? 0,
        assetType,
      };
    });
  }, [accounts, assets, tickers]);

  const filteredRows = rows.filter((row) => {
    const matchesQuery = `${row.symbol} ${row.name}`.toLowerCase().includes(query.toLowerCase());
    const matchesFilter = filter === "ALL" || row.assetType === filter;
    const matchesZero = !hideZero || row.total > 0;
    return matchesQuery && matchesFilter && matchesZero;
  });

  const portfolioValue = rows.reduce((sum, row) => sum + row.value, 0);
  const cryptoValue = rows.filter((row) => row.assetType === "CRYPTO").reduce((sum, row) => sum + row.value, 0);
  const inrRow = rows.find((row) => row.symbol === "INR");
  const cryptoCount = rows.filter((row) => row.assetType === "CRYPTO").length;
  const fiatCount = rows.filter((row) => row.assetType === "FIAT").length;
  const totalAssets = rows.filter((row) => row.total > 0).length;
  const loading = walletLoading || marketLoading;

  return (
    <main className="min-h-screen bg-[#080d12] px-4 py-6 text-white md:px-6 lg:px-8">
      <div className="mx-auto max-w-[1440px]">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Wallet Overview</h1>
            <p className="mt-1 text-sm text-slate-400">Manage your INR and crypto assets in one place.</p>
          </div>
          <div className="flex gap-2">
            <Link href="/wallet/deposit" className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold hover:bg-blue-500">Deposit</Link>
            <Link href="/wallet/withdraw" className="rounded-lg border border-white/10 bg-[#111923] px-5 py-2.5 text-sm font-semibold hover:bg-white/10">Withdraw</Link>
            <Link href="/wallet/transfer" className="rounded-lg border border-white/10 bg-[#111923] px-5 py-2.5 text-sm font-semibold hover:bg-white/10">Transfer</Link>
          </div>
        </div>

        {walletError && <div className="mb-5 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">Unable to load wallet balances. Please sign in and try again.</div>}

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <SummaryCard title="Total Portfolio Value" value={formatInr(portfolioValue)} subtitle="Live INR valuation" />
          <SummaryCard title="INR Balance" value={formatInr(inrRow?.total ?? 0)} subtitle={`Available ${formatInr(inrRow?.available ?? 0)} · Locked ${formatInr(inrRow?.locked ?? 0)}`} />
          <SummaryCard title="Crypto Value" value={formatInr(cryptoValue)} subtitle={`${cryptoCount} crypto assets`} />
          <SummaryCard title="Total Assets" value={String(totalAssets)} subtitle={`${cryptoCount} crypto · ${fiatCount} fiat`} />
        </div>

        <section className="mt-5 overflow-hidden rounded-xl border border-white/10 bg-[#0d141c]">
          <div className="flex flex-col gap-4 border-b border-white/10 p-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h2 className="text-lg font-semibold">Your Assets</h2>
              <p className="mt-1 text-xs text-slate-500">Balances and live INR valuation.</p>
            </div>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search assets..." className="rounded-lg border border-white/10 bg-[#080d12] px-4 py-2 text-sm outline-none placeholder:text-slate-600 focus:border-blue-500" />
              <div className="flex rounded-lg border border-white/10 bg-[#080d12] p-1">
                {(["ALL", "CRYPTO", "FIAT"] as const).map((item) => (
                  <button key={item} onClick={() => setFilter(item)} className={`rounded-md px-3 py-1.5 text-xs font-medium ${filter === item ? "bg-blue-600 text-white" : "text-slate-400 hover:text-white"}`}>{item === "ALL" ? "All" : item === "CRYPTO" ? "Crypto" : "Fiat"}</button>
                ))}
              </div>
              <label className="flex cursor-pointer items-center gap-2 whitespace-nowrap text-xs text-slate-400">
                <input type="checkbox" checked={hideZero} onChange={(event) => setHideZero(event.target.checked)} className="h-3.5 w-3.5 accent-blue-600" />
                Hide zero balances
              </label>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[1050px] text-left text-sm">
              <thead className="border-b border-white/10 text-xs text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-medium">Asset</th>
                  <th className="px-5 py-3 font-medium">Total Balance</th>
                  <th className="px-5 py-3 font-medium">Available</th>
                  <th className="px-5 py-3 font-medium">Locked</th>
                  <th className="px-5 py-3 font-medium">INR Value</th>
                  <th className="px-5 py-3 font-medium">24h Change</th>
                  <th className="px-5 py-3 text-right font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((row) => {
                  const decimals = row.asset?.decimal_places ?? 8;
                  return (
                    <tr key={row.id} className="border-b border-white/5 hover:bg-white/[0.025]">
                      <td className="px-5 py-4"><div className="flex items-center gap-3"><CoinIcon symbol={row.symbol} size={36} /><div><div className="font-semibold">{row.symbol}</div><div className="text-xs text-slate-500">{row.name}</div></div></div></td>
                      <td className="px-5 py-4 font-medium"><div>{formatBalance(row.total, decimals)} <span className="text-xs text-slate-500">{row.symbol}</span></div>{row.assetType === "CRYPTO" && <InrEquivalent value={row.value} />}</td>
                      <td className="px-5 py-4 text-slate-300"><div>{formatBalance(row.available, decimals)} <span className="text-xs text-slate-600">{row.symbol}</span></div>{row.assetType === "CRYPTO" && <InrEquivalent value={row.availableValue} />}</td>
                      <td className="px-5 py-4 text-slate-400"><div>{formatBalance(row.locked, decimals)} <span className="text-xs text-slate-600">{row.symbol}</span></div>{row.assetType === "CRYPTO" && <InrEquivalent value={row.lockedValue} />}</td>
                      <td className="px-5 py-4 font-semibold">{formatInr(row.value)}</td>
                      <td className={`px-5 py-4 ${row.assetType === "FIAT" ? "text-slate-500" : row.change >= 0 ? "text-emerald-400" : "text-red-400"}`}>{row.assetType === "FIAT" ? "—" : `${row.change >= 0 ? "+" : ""}${row.change.toFixed(2)}%`}</td>
                      <td className="px-5 py-4 text-right"><div className="flex justify-end gap-2">{row.assetType === "CRYPTO" ? <><Link href="/buy-sell" className="rounded-md bg-blue-600 px-3 py-2 text-xs font-semibold hover:bg-blue-500">Trade</Link><Link href="/wallet/withdraw" className="rounded-md border border-white/10 bg-[#111923] px-3 py-2 text-xs font-semibold hover:bg-white/10">Send</Link></> : <><Link href="/wallet/deposit" className="rounded-md bg-blue-600 px-3 py-2 text-xs font-semibold hover:bg-blue-500">Deposit</Link><Link href="/wallet/withdraw" className="rounded-md border border-white/10 bg-[#111923] px-3 py-2 text-xs font-semibold hover:bg-white/10">Withdraw</Link></>}</div></td>
                    </tr>
                  );
                })}
                {!loading && filteredRows.length === 0 && <tr><td colSpan={7} className="px-5 py-12 text-center text-sm text-slate-500">No assets found.</td></tr>}
              </tbody>
            </table>
          </div>
          {loading && <div className="px-5 py-10 text-center text-sm text-slate-500">Loading wallet and market data...</div>}
          {!loading && <div className="flex items-center justify-between border-t border-white/10 px-5 py-3 text-xs text-slate-500"><span>Showing {filteredRows.length} of {rows.length} assets</span><span>INR values are based on live market rates · <span className="text-emerald-400">● Live</span></span></div>}
        </section>

        <section className="mt-5 rounded-xl border border-white/10 bg-[#0d141c] p-5">
          <div className="flex items-center justify-between">
            <div><h2 className="text-lg font-semibold">Recent Transactions</h2><p className="mt-1 text-xs text-slate-500">Your latest wallet activity.</p></div>
            <span className="text-xs text-slate-500">Showing {transactions.length}</span>
          </div>

          {transactionsLoading && <div className="mt-5 rounded-lg border border-white/10 py-8 text-center text-sm text-slate-500">Loading transaction history...</div>}
          {!transactionsLoading && transactionsError && <div className="mt-5 rounded-lg border border-red-500/20 bg-red-500/10 py-8 text-center text-sm text-red-300">Unable to load transaction history.</div>}
          {!transactionsLoading && !transactionsError && transactions.length === 0 && <div className="mt-5 rounded-lg border border-dashed border-white/10 py-10 text-center text-sm text-slate-500">No recent transactions to display.</div>}

          {!transactionsLoading && !transactionsError && transactions.length > 0 && (
            <div className="mt-5 overflow-x-auto">
              <table className="w-full min-w-[800px] text-left text-sm">
                <thead className="border-b border-white/10 text-xs text-slate-500">
                  <tr>
                    <th className="px-4 py-3 font-medium">Type</th>
                    <th className="px-4 py-3 font-medium">Asset</th>
                    <th className="px-4 py-3 font-medium">Amount</th>
                    <th className="px-4 py-3 font-medium">Status</th>
                    <th className="px-4 py-3 font-medium">Reference</th>
                    <th className="px-4 py-3 text-right font-medium">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((transaction, index) => {
                    const credit = String(transaction.direction ?? transaction.entry_type).toUpperCase() === "CREDIT";
                    return (
                      <tr key={`${transaction.id ?? transaction.reference}-${index}`} className="border-b border-white/5">
                        <td className="px-4 py-4 font-medium">{formatTransactionType(String(transaction.type ?? "TRANSACTION"))}</td>
                        <td className="px-4 py-4"><div className="flex items-center gap-2"><CoinIcon symbol={String(transaction.asset ?? "INR")} size={28} /><span>{String(transaction.asset ?? "INR")}</span></div></td>
                        <td className={`px-4 py-4 font-semibold ${credit ? "text-emerald-400" : "text-red-400"}`}>{credit ? "+" : "−"}{formatBalance(Number(transaction.amount ?? 0))} {String(transaction.asset ?? "")}</td>
                        <td className="px-4 py-4"><span className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-xs text-emerald-400">{String(transaction.status ?? "UNKNOWN")}</span></td>
                        <td className="px-4 py-4 text-xs text-slate-500">{String(transaction.reference ?? "—")}</td>
                        <td className="px-4 py-4 text-right text-xs text-slate-400">{transaction.created_at ? formatTransactionDate(String(transaction.created_at)) : "—"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

function SummaryCard({ title, value, subtitle }: { title: string; value: string; subtitle: string }) {
  return <div className="rounded-xl border border-white/10 bg-[#0d141c] p-5"><div className="text-sm text-slate-400">{title}</div><div className="mt-2 text-2xl font-bold tracking-tight">{value}</div><div className="mt-3 text-xs text-slate-500">{subtitle}</div></div>;
}
