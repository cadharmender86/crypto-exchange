"use client";

export default function AdBanner() {
  return (
    <section className="w-full rounded-xl border border-slate-800 bg-gradient-to-r from-blue-950 via-slate-900 to-indigo-950 p-6 flex flex-col md:flex-row items-center justify-between gap-4">
      <div>
        <p className="text-sm text-blue-400">BitNova Promotion</p>
        <h2 className="text-2xl font-bold text-white mt-1">
          Trade Crypto Smarter With BitNova
        </h2>
        <p className="text-slate-400 mt-2">
          Secure wallet, instant buy/sell and advanced trading experience.
        </p>
      </div>

      <button className="rounded-lg bg-blue-600 px-6 py-3 text-white font-semibold hover:bg-blue-700">
        Start Trading
      </button>
    </section>
  );
}
