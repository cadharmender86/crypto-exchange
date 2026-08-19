"use client";

type CryptoPortfolioProps = {
  currentValue?: number;
  netCost?: number;
  profitLoss?: number;
  tradingVolume?: number;
  showBalance?: boolean;
};

export default function CryptoPortfolio({
  currentValue = 0,
  netCost = 0,
  profitLoss = 0,
  tradingVolume = 0,
  showBalance = true,
}: CryptoPortfolioProps) {
  const profitPercentage =
    netCost > 0
      ? ((profitLoss / netCost) * 100).toFixed(2)
      : "0.00";

  return (
    <section className="rounded-lg border border-white/[0.06] bg-[#10161d] px-4 py-3 shadow-[0_8px_25px_rgba(0,0,0,.12)]">
      <h2 className="mb-2 text-xs font-bold text-white">
        Crypto Portfolio
      </h2>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-5 md:gap-6">

        {/* Current Value */}
        <div>
          <p className="text-[10px] text-slate-400">
            Current Value
          </p>

          <p className="mt-1 text-sm font-bold">
            {showBalance
              ? `₹ ${currentValue.toLocaleString("en-IN")}`
              : "₹ ••••••"}
          </p>

          <p className="text-[10px] text-slate-300">
            {showBalance ? "= 0.081234 BTC" : "= ••••••"}
          </p>
        </div>

        {/* Net Cost */}
        <div>
          <p className="text-[10px] text-slate-400">
            Net Cost
          </p>

          <p className="mt-1 text-sm font-bold">
            {showBalance
              ? `₹ ${netCost.toLocaleString("en-IN")}`
              : "₹ ••••••"}
          </p>

          <p className="text-[10px] text-slate-300">
            {showBalance ? "= 0.075012 BTC" : "= ••••••"}
          </p>
        </div>

        {/* Profit / Loss */}
        <div>
          <p className="text-[10px] text-slate-400">
            Profit / Loss
          </p>

          <p className="mt-1 text-sm font-bold text-emerald-400">
            {showBalance
              ? `₹ ${profitLoss.toLocaleString("en-IN")}`
              : "₹ ••••••"}
          </p>

          <p className="text-[10px] font-semibold text-emerald-400">
            {showBalance
              ? `${profitPercentage}%`
              : "••••"}
          </p>
        </div>

        {/* 24h Change */}
        <div>
          <p className="text-[10px] text-slate-400">
            24h Change
          </p>

          <p className="mt-1 text-sm font-bold text-emerald-400">
            {showBalance
              ? "₹ 18,250"
              : "₹ ••••••"}
          </p>

          <p className="text-[10px] font-semibold text-emerald-400">
            {showBalance ? "2.45%" : "••••"}
          </p>
        </div>

        {/* Trading Volume */}
        <div>
          <p className="text-[10px] text-slate-400">
            30 Days Trading Volume
          </p>

          <p className="mt-1 text-sm font-bold">
            {showBalance
              ? `₹ ${tradingVolume.toLocaleString("en-IN")}`
              : "₹ ••••••"}
          </p>
        </div>

      </div>
    </section>
  );
}