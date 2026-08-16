import { markets } from "@/lib/marketData";

export default function MarketTicker() {
  return (
    <section className="border-b border-white/10 bg-[#0a0f1b]">
      <div className="mx-auto flex max-w-7xl gap-8 overflow-x-auto px-4 py-3 lg:px-8">

        {markets.map((market) => (
          <div
            key={market.symbol}
            className="flex min-w-fit items-center gap-3"
          >
            <span className="text-sm font-semibold text-white">
              {market.symbol}
            </span>

            <span className="text-sm text-gray-300">
              ₹{market.price.toLocaleString("en-IN")}
            </span>

            <span
              className={`text-xs font-medium ${
                market.change >= 0
                  ? "text-green-400"
                  : "text-red-400"
              }`}
            >
              {market.change >= 0 ? "+" : ""}
              {market.change}%
            </span>
          </div>
        ))}

      </div>
    </section>
  );
}