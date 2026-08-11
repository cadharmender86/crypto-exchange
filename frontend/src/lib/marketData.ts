export interface Market {
  symbol: string;
  name: string;
  price: number;
  change: number;
}

export const markets: Market[] = [
  {
    symbol: "BTC/INR",
    name: "Bitcoin",
    price: 9850000,
    change: 2.41,
  },
  {
    symbol: "ETH/INR",
    name: "Ethereum",
    price: 325000,
    change: 1.82,
  },
  {
    symbol: "USDT/INR",
    name: "Tether",
    price: 96.45,
    change: 0.15,
  },
  {
    symbol: "SOL/INR",
    name: "Solana",
    price: 14500,
    change: -1.12,
  },
  {
    symbol: "XRP/INR",
    name: "XRP",
    price: 210,
    change: 3.26,
  },
];