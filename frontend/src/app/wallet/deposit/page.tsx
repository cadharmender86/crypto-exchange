"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import CoinIcon from "@/components/common/CoinIcon";
import { getMarketAssets, type MarketAsset } from "@/services/market.service";
import { getMyWallets, getWalletAddresses, type WalletAddress } from "@/services/wallet-address.service";

export default function DepositPage() {
  const [assets, setAssets] = useState<MarketAsset[]>([]);
  const [addresses, setAddresses] = useState<WalletAddress[]>([]);
  const [selectedAssetId, setSelectedAssetId] = useState("");
  const [selectedNetwork, setSelectedNetwork] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    Promise.all([getMarketAssets(), getMyWallets()])
      .then(async ([assetData, walletData]) => {
        if (!active) return;

        const depositAssets = assetData.filter(
          (asset) => asset.is_active && asset.deposit_enabled && asset.asset_type.toUpperCase() !== "FIAT",
        );
        setAssets(depositAssets);

        const wallet = walletData.find((item) => item.wallet_type.toUpperCase() === "CUSTOMER" && item.status === "ACTIVE") ?? walletData[0];
        if (!wallet) {
          setError("No active wallet is available for your account.");
          return;
        }

        const walletAddresses = await getWalletAddresses(wallet.id);
        if (!active) return;
        setAddresses(walletAddresses.filter((item) => item.status.toUpperCase() === "ACTIVE" && item.address_type.toUpperCase() === "DEPOSIT"));
      })
      .catch((err) => {
        if (active) setError(err?.message || "Unable to load deposit information.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const effectiveAssetId = selectedAssetId || assets[0]?.id || "";

  const availableNetworks = useMemo(
    () => addresses.filter((item) => item.asset_id === effectiveAssetId),
    [addresses, effectiveAssetId],
  );

  const effectiveNetwork = selectedNetwork || availableNetworks[0]?.network || "";

  const selectedAddress = useMemo(
    () => availableNetworks.find((item) => item.network === effectiveNetwork) ?? availableNetworks[0],
    [availableNetworks, effectiveNetwork],
  );

  const selectedAsset = assets.find((asset) => asset.id === effectiveAssetId);

  const copyAddress = async () => {
    if (!selectedAddress) return;
    await navigator.clipboard.writeText(selectedAddress.address);
  };

  if (loading) {
    return <main className="min-h-screen bg-[#080d12] px-4 py-8 text-white md:px-8"><div className="mx-auto max-w-3xl rounded-xl border border-white/10 bg-[#0d141c] p-8 text-center text-sm text-slate-400">Loading deposit addresses...</div></main>;
  }

  return (
    <main className="min-h-screen bg-[#080d12] px-4 py-6 text-white md:px-8">
      <div className="mx-auto max-w-3xl">
        <div className="mb-6">
          <Link href="/wallet" className="text-sm text-blue-400 hover:text-blue-300">← Back to Wallet</Link>
          <h1 className="mt-4 text-2xl font-bold">Deposit Crypto</h1>
          <p className="mt-1 text-sm text-slate-400">Send crypto to your BitNova deposit address.</p>
        </div>

        {error && <div className="mb-5 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</div>}

        <section className="rounded-xl border border-white/10 bg-[#0d141c] p-6">
          <div className="grid gap-5 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">Asset</label>
              <select value={effectiveAssetId} onChange={(event) => { setSelectedAssetId(event.target.value); setSelectedNetwork(""); }} className="w-full rounded-lg border border-white/10 bg-[#080d12] px-4 py-3 text-sm text-white outline-none focus:border-blue-500">
                {assets.map((asset) => <option key={asset.id} value={asset.id}>{asset.symbol} — {asset.name}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">Network</label>
              <select value={effectiveNetwork} onChange={(event) => setSelectedNetwork(event.target.value)} disabled={availableNetworks.length === 0} className="w-full rounded-lg border border-white/10 bg-[#080d12] px-4 py-3 text-sm text-white outline-none focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-50">
                {availableNetworks.length === 0 ? <option value="">No network available</option> : availableNetworks.map((item) => <option key={item.id} value={item.network}>{item.network}</option>)}
              </select>
            </div>
          </div>

          {selectedAddress ? (
            <div className="mt-6 rounded-xl border border-white/10 bg-[#080d12] p-5">
              <div className="flex items-center gap-3">
                {selectedAsset && <CoinIcon symbol={selectedAsset.symbol} size={40} />}
                <div>
                  <div className="font-semibold">{selectedAsset?.symbol ?? "Crypto"} deposit address</div>
                  <div className="text-xs text-slate-500">Network: {selectedAddress.network}</div>
                </div>
              </div>

              <div className="mt-5">
                <div className="mb-2 text-xs text-slate-500">Your deposit address</div>
                <div className="flex flex-col gap-3 sm:flex-row">
                  <div className="min-w-0 flex-1 break-all rounded-lg border border-white/10 bg-[#0d141c] px-4 py-3 font-mono text-sm text-slate-200">{selectedAddress.address}</div>
                  <button onClick={copyAddress} className="rounded-lg bg-blue-600 px-5 py-3 text-sm font-semibold hover:bg-blue-500">Copy</button>
                </div>
              </div>

              <div className="mt-5 rounded-lg border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-amber-200">
                <div className="font-semibold">Important</div>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-xs text-amber-200/80">
                  <li>Send only {selectedAsset?.symbol ?? "this asset"} using the selected {selectedAddress.network} network.</li>
                  <li>Sending an unsupported asset or network may result in permanent loss.</li>
                  <li>Your balance is credited after the required blockchain confirmations and deposit processing.</li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="mt-6 rounded-xl border border-dashed border-white/10 p-8 text-center">
              <div className="font-medium">No deposit address assigned</div>
              <p className="mt-2 text-sm text-slate-500">A deposit address for this asset/network has not been assigned to your wallet yet.</p>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
