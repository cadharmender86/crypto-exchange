import Link from "next/link";
import { markets } from "@/lib/marketData";

export default function MarketsPage() {
  return (
    <main className="min-h-screen bg-[#070b14] px-4 py-10 text-white lg:px-8">
      <div className="mx-auto max-w-7xl">
        <Link href="/" className="text-sm text-blue-400">← BitNova</Link>
        <h1 className="mt-4 text-4xl font-bold">Markets</h1>
        <p className="mt-2 text-gray-400">Explore supported market pairs and continue to the customer app to trade.</p>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {markets.map((market) => (
            <div key={market.symbol} className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">{market.symbol}</h2>
                <span className={market.change >= 0 ? "text-green-400" : "text-red-400"}>{market.change >= 0 ? "+" : ""}{market.change}%</span>
              </div>
              <p className="mt-2 text-sm text-gray-400">{market.name}</p>
              <p className="mt-5 text-lg font-semibold text-white">₹{market.price.toLocaleString("en-IN")}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
