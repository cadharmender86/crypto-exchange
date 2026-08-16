import Link from "next/link";
import { customerUrl } from "@/lib/site";

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-[#070b14]">
      <div className="absolute left-1/2 top-0 h-[500px] w-[700px] -translate-x-1/2 rounded-full bg-blue-600/10 blur-[120px]" />
      <div className="relative mx-auto grid max-w-7xl items-center gap-14 px-4 py-24 lg:grid-cols-2 lg:px-8 lg:py-32">
        <div>
          <div className="mb-6 inline-flex rounded-full border border-blue-400/20 bg-blue-400/10 px-4 py-2 text-sm text-blue-300">India&apos;s next-generation crypto platform</div>
          <h1 className="max-w-3xl text-5xl font-bold leading-tight tracking-tight text-white md:text-6xl">Trade crypto.<br /><span className="text-blue-400">Simple. Secure. Fast.</span></h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-gray-400">Buy, sell and trade digital assets with a powerful platform designed for Indian crypto users.</p>
          <div className="mt-8 flex flex-wrap gap-4">
            <a href={customerUrl("/register")} className="rounded-xl bg-blue-500 px-7 py-3.5 font-semibold text-white transition hover:bg-blue-600">Start Trading</a>
            <Link href="/markets" className="rounded-xl border border-white/10 bg-white/5 px-7 py-3.5 font-semibold text-white hover:bg-white/10">Explore Markets</Link>
          </div>
          <div className="mt-10 flex flex-wrap gap-8">
            <div><div className="text-2xl font-bold text-white">100+</div><div className="text-sm text-gray-500">Crypto Assets</div></div>
            <div><div className="text-2xl font-bold text-white">24/7</div><div className="text-sm text-gray-500">Trading</div></div>
            <div><div className="text-2xl font-bold text-white">Secure</div><div className="text-sm text-gray-500">Infrastructure</div></div>
          </div>
        </div>

        <div className="relative">
          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-5 shadow-2xl shadow-blue-900/20">
            <div className="mb-5 flex items-center justify-between">
              <div><p className="text-sm text-gray-400">BTC/INR</p><h2 className="mt-1 text-3xl font-bold text-white">Market preview</h2></div>
              <span className="rounded-lg bg-white/5 px-3 py-2 text-sm text-gray-400">Indicative</span>
            </div>
            <div className="flex h-64 items-end gap-2">
              {[40, 50, 45, 65, 58, 72, 68, 80, 75, 90, 84, 96].map((height, index) => <div key={index} className="flex-1 rounded-t bg-blue-500/70" style={{ height: `${height}%` }} />)}
            </div>
            <div className="mt-6 grid grid-cols-2 gap-3">
              <a href={customerUrl("/buy-sell")} className="rounded-xl bg-green-500 py-3 text-center font-semibold text-white hover:bg-green-600">Buy</a>
              <a href={customerUrl("/buy-sell")} className="rounded-xl bg-red-500 py-3 text-center font-semibold text-white hover:bg-red-600">Sell</a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
