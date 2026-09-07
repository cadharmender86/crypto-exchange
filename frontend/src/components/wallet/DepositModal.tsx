"use client";

import { useEffect, useState } from "react";
import QRCode from "react-qr-code";
import { X, Copy, CheckCircle, Wallet } from "lucide-react";

import type { ReceiveAddressResponse } from "@/services/wallet.service";

type DepositModalProps = {
  open: boolean;
  asset: {
    symbol: string;
    name: string;
    is_fiat: boolean;
  } | null;
  onClose: () => void;

  // NEW: Crypto receive props
    receiveAddress: ReceiveAddressResponse | null;
    loading: boolean;
    generating: boolean;
    onGenerate: (network: string) => void;
};

export default function DepositModal({
  open,
  asset,
  onClose,
  receiveAddress,
  loading,
  generating,
  onGenerate,
}: DepositModalProps) {
  // const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [selectedNetwork, setSelectedNetwork] = useState("");

  const NETWORKS: Record<string, string[]> = {
    USDT: ["ETHEREUM_SEPOLIA"],
    ETH: ["ETHEREUM_SEPOLIA"],
    BITNOVA: ["ETHEREUM_SEPOLIA"],
    BTC: ["BITCOIN_TESTNET"],   // Later
  };

  const depositAddress = receiveAddress?.address ?? "";
  const network = receiveAddress?.network ?? "";

  // ✅ Hook BEFORE any return
  useEffect(() => {
    if (!open || !asset) return;

    setCopied(false);
    setSelectedNetwork(NETWORKS[asset.symbol]?.[0] ?? "");
  }, [open, asset]);

  // ✅ Return comes AFTER hooks
  if (!open || !asset) return null;

  const copyAddress = async () => {
    await navigator.clipboard.writeText(depositAddress);
    setCopied(true);

    setTimeout(() => setCopied(false), 2000);
  };


  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div className="w-full max-w-lg rounded-2xl border border-white/10 bg-[#111827] p-6 shadow-2xl">

        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-white">
              Deposit {asset.symbol}
            </h2>

            <p className="text-sm text-gray-400">{asset.name}</p>
          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-2 text-gray-400 hover:bg-white/10 hover:text-white"
          >
            <X size={20} />
          </button>
        </div>

        {/* Loading */}
        {loading ? (
          <div className="py-10 text-center text-gray-400">
            Loading wallet address...
          </div>
        ) : !receiveAddress?.generated ? (

          /* First time user */
          <div className="space-y-5 text-center">

            <div className="rounded-xl border border-dashed border-zinc-700 p-8">
              <Wallet className="mx-auto mb-3 text-green-500" size={40} />

              <h3 className="text-lg font-semibold text-white">
                Generate Deposit Address
              </h3>

              <p className="mt-2 text-sm text-gray-400">
                Your personal {asset.symbol} deposit wallet will be created once and
                reused for future deposits.
              </p>
            </div>
          </div>
        ) : (

          /* Existing address */
          <div className="space-y-5">

            {/* Network dropdown is always visible */}
            <div>
              <p className="mb-1 text-xs uppercase tracking-wide text-gray-500">
                Network
              </p>

              <select
                value={selectedNetwork}
                onChange={(e) => setSelectedNetwork(e.target.value)}
                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-white"
              >
                {NETWORKS[asset.symbol]?.map((item) => (
                  <option key={item}  value={item}>
                    {item.replaceAll("_", " ")}
                  </option>
                ))}
              </select>  
            </div>

            {/* Generate button */}
            {!receiveAddress && (
              <button
                onClick={() => onGenerate(selectedNetwork)}
                disabled={generating || !selectedNetwork}
                className="w-full rounded-lg bg-green-600 py-3 font-medium text-white hover:bg-green-500 disabled:opacity-60"
              >
                {generating ? "Generating Address..." : "Generate Deposit Address"}
              </button>
            )}

            {/* Address generated */}
            {receiveAddress && (
              <>
                <div className="flex justify-center rounded-xl bg-white p-4">
                  <QRCode value={depositAddress} size={180} />
                </div>
                  
                <div>
                  <p className="mb-1 text-xs uppercase tracking-wide text-gray-500">
                    Network
                  </p>

                  <div className="inline-block rounded-lg bg-blue-500/20 px-3 py-2 text-sm font-medium text-blue-300">
                    {network.replaceAll("_", " ")}
                  </div>
                </div>

                <div>
                  <p className="mb-1 text-xs uppercase tracking-wide text-gray-500">
                    Deposit Address
                  </p>

                  <div className="break-all rounded-lg border border-zinc-700 bg-zinc-900 p-3 font-mono text-sm text-green-400">
                    {depositAddress}
                  </div>
                </div>

                {/* Copy */}
                <button
                  onClick={copyAddress}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-green-600 py-3 font-medium text-white hover:bg-green-500"
                >
                  {copied ? <CheckCircle size={18} /> : <Copy size={18} />}
                  {copied ? "Copied!" : "Copy Address"}
                </button>
              </>
            )}

            {/* Warning */}
            <div className="rounded-lg border border-yellow-600 bg-yellow-900/20 p-4 text-sm text-yellow-300">
              <p className="mb-2 font-semibold">Important</p>

              <ul className="list-disc space-y-1 pl-5">
                <li>Send only {asset.symbol} to this address.</li>
                <li>Use the {network} network only.</li>
                <li>Sending assets on another network may permanently lose funds.</li>
                <li>Funds are credited after blockchain confirmations.</li>
              </ul>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}