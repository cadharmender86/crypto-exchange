"use client";

type CoinIconProps = {
  symbol: string;
  size?: number;
};

function BitcoinIcon() {
  return (
    <svg viewBox="0 0 32 32" className="h-full w-full">
      <circle cx="16" cy="16" r="16" fill="#f7931a" />
      <path d="M20.8 13.1c.3-2-1.2-3.1-3.3-3.8l.7-2.7-1.7-.4-.7 2.6-1.4-.3.7-2.6-1.7-.4-.7 2.7-1.1-.3v-.1l-2.4-.6-.5 1.8s1.3.3 1.3.3c.7.2.8.6.8 1l-.8 3.2c.1 0 .2.1.3.1l-.3-.1-1.1 4.5c-.1.2-.3.5-.8.4l-1.3-.3-.8 1.9 2.3.6 1.3.3-.7 2.8 1.7.4.7-2.7 1.4.4-.7 2.7 1.7.4.7-2.8c2.8.5 4.9.3 5.8-2.2.7-2 .1-3.2-1.5-4 .9-.2 1.7-.9 1.9-2.2Zm-3.8 5.3c-.5 2-3.8.9-4.9.7l.9-3.6c1.1.3 4.5.8 4 2.9Zm.5-5.4c-.5 1.8-3.2.9-4.1.7l.8-3.3c.9.2 3.8.6 3.3 2.6Z" fill="white" />
    </svg>
  );
}

function EthereumIcon() {
  return (
    <svg viewBox="0 0 32 32" className="h-full w-full">
      <circle cx="16" cy="16" r="16" fill="#627eea" />
      <path d="M16 4.5 9.2 16l6.8 4 6.8-4L16 4.5Z" fill="#d8defa" />
      <path d="m16 4.5-6.8 11.4 6.8-3.1V4.5Z" fill="white" opacity=".85" />
      <path d="M16 21.3 9.2 17l6.8 10.5L22.8 17l-6.8 4.3Z" fill="#c0c9f5" />
      <path d="M16 21.3v6.2L22.8 17 16 21.3Z" fill="#a8b4ed" />
    </svg>
  );
}

function TetherIcon() {
  return (
    <svg viewBox="0 0 32 32" className="h-full w-full">
      <circle cx="16" cy="16" r="16" fill="#26a17b" />
      <path d="M8.5 8.2h15v3.1h-5.65v2.25c4.25.25 7.15 1.05 7.15 2.1 0 1.3-4.03 2.35-9 2.35s-9-1.05-9-2.35c0-1.05 2.9-1.85 7.15-2.1v-2.25H8.5V8.2Z" fill="white" />
      <path d="M16 18c4.97 0 9-1.05 9-2.35v6.1c0 1.45-4.03 2.6-9 2.6s-9-1.15-9-2.6v-6.1C7 16.95 11.03 18 16 18Z" fill="white" opacity=".98" />
      <path d="M16 18v6.35" stroke="#26a17b" strokeWidth="1.2" />
    </svg>
  );
}

function SolanaIcon() {
  return (
    <svg viewBox="0 0 32 32" className="h-full w-full">
      <circle cx="16" cy="16" r="16" fill="#111827" />
      <path d="M8 10.5c.3-.4.7-.6 1.2-.6h13.3c.8 0 1.2.9.6 1.5l-2.1 2.1c-.3.3-.7.5-1.1.5H6.6c-.8 0-1.2-.9-.6-1.5L8 10.5Z" fill="#9945ff" />
      <path d="M8 17.1c.3-.4.7-.6 1.2-.6h13.3c.8 0 1.2.9.6 1.5L21 20.1c-.3.3-.7.5-1.1.5H6.6c-.8 0-1.2-.9-.6-1.5L8 17.1Z" fill="#14f195" />
      <path d="M8 23.7c.3-.4.7-.6 1.2-.6h13.3c.8 0 1.2.9.6 1.5L21 26.7c-.3.3-.7.5-1.1.5H6.6c-.8 0-1.2-.9-.6-1.5L8 23.7Z" fill="#00c2ff" />
    </svg>
  );
}

function InrIcon() {
  return (
    <svg viewBox="0 0 32 32" className="h-full w-full">
      <circle cx="16" cy="16" r="16" fill="#f4f6f8" />
      <path d="M9.5 9.5h12.3M9.5 13.1h12.3M16.9 13.1c-.6 4-3.1 5.4-6.1 5.4h-1l8.4 4.8" fill="none" stroke="#1f2937" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

const iconMap: Record<string, () => React.ReactNode> = {
  BTC: BitcoinIcon,
  ETH: EthereumIcon,
  USDT: TetherIcon,
  SOL: SolanaIcon,
  INR: InrIcon,
};

const fallbackColors: Record<string, string> = {
  XRP: "#23292f",
  ADA: "#0033ad",
  DOGE: "#c2a633",
  BNB: "#f3ba2f",
};

export default function CoinIcon({ symbol, size = 32 }: CoinIconProps) {
  const normalizedSymbol = symbol.toUpperCase();
  const Icon = iconMap[normalizedSymbol];

  if (Icon) {
    return (
      <span className="inline-flex shrink-0 overflow-hidden rounded-full" style={{ width: size, height: size }}>
        <Icon />
      </span>
    );
  }

  return (
    <span className="inline-flex shrink-0 items-center justify-center rounded-full text-[10px] font-bold text-white" style={{ width: size, height: size, backgroundColor: fallbackColors[normalizedSymbol] || "#374151" }}>
      {normalizedSymbol.slice(0, 3)}
    </span>
  );
}
