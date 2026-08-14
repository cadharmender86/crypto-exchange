"use client";

type CryptoPortfolioProps = {
  currentValue?: number;
  netCost?: number;
  profitLoss?: number;
  tradingVolume?: number;
};

export default function CryptoPortfolio({
  currentValue = 0,
  netCost = 0,
  profitLoss = 0,
  tradingVolume = 0,
}: CryptoPortfolioProps) {
  const profitPercentage =
    netCost > 0 ? ((profitLoss / netCost) * 100).toFixed(2) : "0.00";

  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-6">
      <h2 className="mb-5 text-lg font-semibold text-white">
        Crypto Portfolio
      </h2>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
        <div>
          <p className="text-sm text-gray-400">Current Value</p>
          <h3 className="mt-2 text-2xl font-bold text-white">
            ₹ {currentValue.toLocaleString("en-IN")}
          </h3>
        </div>

        <div>
          <p className="text-sm text-gray-400">Net Cost</p>
          <h3 className="mt-2 text-2xl font-bold text-white">
            ₹ {netCost.toLocaleString("en-IN")}
          </h3>
        </div>

        <div>
          <p className="text-sm text-gray-400">Profit / Loss</p>
          <h3 className={profitLoss >= 0 ? "mt-2 text-2xl font-bold text-green-400" : "mt-2 text-2xl font-bold text-red-400"}>
            ₹ {profitLoss.toLocaleString("en-IN")}
          </h3>
          <span className="text-sm text-gray-400">{profitPercentage}%</span>
        </div>

        <div>
          <p className="text-sm text-gray-400">30 Days Trading Volume</p>
          <h3 className="mt-2 text-2xl font-bold text-white">
            ₹ {tradingVolume.toLocaleString("en-IN")}
          </h3>
        </div>
      </div>
    </section>
  );
}
