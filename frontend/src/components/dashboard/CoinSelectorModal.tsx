"use client";

import { useState } from "react";

type Props = {
  open: boolean;
  onClose: () => void;
  onSelect: (coin: string) => void;
};

const coins = [
  { symbol: "BTC", name: "Bitcoin" },
  { symbol: "ETH", name: "Ethereum" },
  { symbol: "SOL", name: "Solana" },
  { symbol: "XRP", name: "Ripple" },
  { symbol: "ADA", name: "Cardano" },
  { symbol: "DOGE", name: "Dogecoin" },
  { symbol: "DOT", name: "Polkadot" },
  { symbol: "AVAX", name: "Avalanche" },
  { symbol: "BNB", name: "BNB" },
];

export default function CoinSelectorModal({ open, onClose, onSelect }: Props) {
  const [search, setSearch] = useState("");

  if (!open) return null;

  const filtered = coins.filter((coin) =>
    coin.symbol.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div className="w-full max-w-md rounded-xl border border-gray-700 bg-[#111318] p-6">
        <div className="mb-4 flex justify-between">
          <h3 className="text-lg font-semibold text-white">Select Coin</h3>
          <button onClick={onClose} className="text-gray-400">✕</button>
        </div>

        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search coin"
          className="mb-4 w-full rounded-lg border border-gray-700 bg-transparent p-3 text-white"
        />

        <div className="space-y-2">
          {filtered.map((coin) => (
            <button
              key={coin.symbol}
              onClick={() => {
                onSelect(coin.symbol);
                onClose();
              }}
              className="flex w-full justify-between rounded-lg bg-gray-900 p-3 text-left text-white hover:bg-gray-800"
            >
              <span>{coin.name}</span>
              <span>{coin.symbol}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
