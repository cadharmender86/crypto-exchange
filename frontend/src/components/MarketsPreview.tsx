import Link from "next/link";
import { markets } from "@/lib/marketData";

export default function MarketsPreview() {
  return (
    <section className="bg-[#0a0f1b] py-24 lg:py-28">
      <div className="mx-auto max-w-[1400px] px-6 lg:px-10">
        <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
              Markets
            </p>
            <h2 className="mt-4 text-4xl font-bold tracking-tight text-white md:text-5xl">
              Explore popular crypto markets
            </h2>
            <p className="mt-5 max-w-2xl text-base leading-7 text-gray-400 md:text-lg">
              Track popular INR markets and move from discovery to trading when
              you are ready.
            </p>
          </div>

          <Link
            href="/markets"
            className="inline-flex w-fit items-center rounded-xl border border-white/10 bg-white/5 px-5 py-3 font-semibold text-white transition hover:border-blue-400/30 hover:bg-white/10"
          >
            View all markets <span className="ml-2">→</span>
          </Link>
        </div>

        <div className="mt-12 overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03]">
          <div className="hidden grid-cols-[1.5fr_1fr_1fr_120px] border-b border-white/10 px-7 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500 md:grid">
            <span>Market</span>
            <span>Price</span>
            <span>24h change</span>
            <span />
          </div>

          {markets.map((market) => (
            <div
              key={market.symbol}
              className="grid gap-4 border-b border-white/10 px-6 py-6 last:border-b-0 md:grid-cols-[1.5fr_1fr_1fr_120px] md:items-center md:px-7"
            >
              <div>
                <div className="text-lg font-semibold text-white">
                  {market.symbol}
                </div>
                <div className="mt-1 text-sm text-gray-500">{market.name}</div>
              </div>

              <div className="text-lg font-semibold text-white">
                ₹{market.price.toLocaleString("en-IN")}
              </div>

              <div
                className={
                  market.change >= 0
                    ? "font-semibold text-green-400"
                    : "font-semibold text-red-400"
                }
              >
                {market.change >= 0 ? "+" : ""}
                {market.change}%
              </div>

              <Link
                href="/markets"
                className="w-fit rounded-lg border border-white/10 px-4 py-2 text-sm font-semibold text-gray-200 transition hover:border-blue-400/40 hover:text-blue-300"
              >
                Trade →
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
