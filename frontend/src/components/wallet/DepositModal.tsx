"use client";

import { useEffect, useState } from "react";
import QRCode from "react-qr-code";
import { X, Copy, CheckCircle } from "lucide-react";

import { getDepositAddress } from "@/services/deposit.service";

type DepositModalProps = {
  open: boolean;
  asset: {
    symbol: string;
    name: string;
    is_fiat: boolean;
  } | null;
  onClose: () => void;
};

export default function DepositModal({
  open,
  asset,
  onClose,
}: DepositModalProps) {
  const [loading, setLoading] = useState(false);
  const [depositAddress, setDepositAddress] = useState("");
  const [network, setNetwork] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!open || !asset || asset.is_fiat) return;

    setLoading(true);
    setDepositAddress("");
    setNetwork("");
    setCopied(false);

    getDepositAddress(asset.symbol)
      .then((data) => {
        setDepositAddress(data.address);
        setNetwork(data.network);
      })
      .catch((error) => {
        console.error("Unable to load deposit address", error);
      })
      .finally(() => setLoading(false));
  }, [open, asset]);

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
            Loading deposit address...
          </div>
        ) : (
          <div className="space-y-5">

            {/* QR Code */}
            <div className="flex justify-center rounded-xl bg-white p-4">
              <QRCode value={depositAddress} size={180} />
            </div>

            {/* Network */}
            <div>
              <p className="mb-1 text-xs uppercase tracking-wide text-gray-500">
                Network
              </p>

              <div className="inline-block rounded-lg bg-blue-500/20 px-3 py-2 text-sm font-medium text-blue-300">
                {network}
              </div>
            </div>

            {/* Address */}
            <div>
              <p className="mb-1 text-xs uppercase tracking-wide text-gray-500">
                Deposit Address
              </p>

              <div className="break-all rounded-lg border border-zinc-700 bg-zinc-900 p-3 font-mono text-sm text-white">
                {depositAddress}
              </div>
            </div>

            {/* Copy Button */}
            <button
              onClick={copyAddress}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-green-600 py-3 font-medium text-white transition hover:bg-green-500"
            >
              {copied ? (
                <CheckCircle size={18} />
              ) : (
                <Copy size={18} />
              )}

              {copied ? "Copied" : "Copy Address"}
            </button>

            {/* Warning */}
            <div className="rounded-lg border border-yellow-600 bg-yellow-900/20 p-4 text-sm text-yellow-300">
              <p className="mb-2 font-semibold">Important</p>

              <ul className="list-disc space-y-1 pl-5">
                <li>Send only {asset.symbol} to this address.</li>
                <li>Use the {network} network only.</li>
                <li>Sending funds on another network may result in permanent loss.</li>
                <li>Funds are credited after blockchain confirmations.</li>
              </ul>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}