"use client";

type CoinIconProps = {
  symbol: string;
  size?: number;
};

const coinColors: Record<string, string> = {
  BTC: "#f7931a",
  ETH: "#627eea",
  USDT: "#26a17b",
  SOL: "#9945ff",
  XRP: "#23292f",
  ADA: "#0033ad",
  DOGE: "#c2a633",
  BNB: "#f3ba2f",
};

export default function CoinIcon({ symbol, size = 32 }: CoinIconProps) {
  return (
    <div
      className="flex items-center justify-center rounded-full text-xs font-bold text-white"
      style={{
        width: size,
        height: size,
        backgroundColor: coinColors[symbol] || "#374151",
      }}
    >
      {symbol.slice(0, 3)}
    </div>
  );
}
