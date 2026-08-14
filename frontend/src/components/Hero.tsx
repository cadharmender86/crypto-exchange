import Link from "next/link";

export default function Hero() {
  return (
    <section className="relative min-h-[720px] overflow-hidden bg-[#070b14] lg:min-h-[760px]">
      <div className="absolute left-1/3 top-0 h-[600px] w-[900px] -translate-x-1/2 rounded-full bg-blue-600/10 blur-[140px]" />
      <div className="absolute bottom-0 right-0 h-[420px] w-[520px] rounded-full bg-blue-500/5 blur-[120px]" />

      <div className="relative mx-auto grid min-h-[720px] max-w-[1400px] items-center gap-16 px-6 py-20 lg:min-h-[760px] lg:grid-cols-[1.05fr_0.95fr] lg:px-10 lg:py-24">
        <div className="max-w-3xl">
          <div className="mb-7 inline-flex rounded-full border border-blue-400/20 bg-blue-400/10 px-4 py-2 text-sm font-medium text-blue-300">
            India's next-generation crypto platform
          </div>

          <h1 className="text-5xl font-bold leading-[1.05] tracking-tight text-white sm:text-6xl lg:text-7xl xl:text-8xl">
            Trade crypto.
            <br />
            <span className="text-blue-400">Simple. Secure. Fast.</span>
          </h1>

          <p className="mt-8 max-w-2xl text-lg leading-8 text-gray-400 lg:text-xl lg:leading-9">
            Buy, sell and manage digital assets with a powerful platform built
            for Indian crypto users.
          </p>

          <div className="mt-10 flex flex-wrap gap-4">
            <Link
              href="/register"
              className="rounded-xl bg-blue-500 px-8 py-4 font-semibold text-white transition hover:bg-blue-600"
            >
              Start Trading
            </Link>
            <Link
              href="/markets"
              className="rounded-xl border border-white/10 bg-white/5 px-8 py-4 font-semibold text-white transition hover:bg-white/10"
            >
              Explore Markets
            </Link>
          </div>

          <div className="mt-14 grid max-w-xl grid-cols-3 gap-6 border-t border-white/10 pt-7">
            <div>
              <div className="text-3xl font-bold text-white">100+</div>
              <div className="mt-1 text-sm text-gray-500">Crypto Assets</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">24/7</div>
              <div className="mt-1 text-sm text-gray-500">Trading</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white">Secure</div>
              <div className="mt-1 text-sm text-gray-500">Infrastructure</div>
            </div>
          </div>
        </div>

        <div className="relative lg:pl-4">
          <div className="absolute -inset-6 rounded-[2.5rem] bg-blue-500/5 blur-2xl" />
          <div className="relative rounded-[2rem] border border-white/10 bg-[#101725]/90 p-6 shadow-2xl shadow-blue-900/20 backdrop-blur sm:p-7">
            <div className="mb-7 flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-400">BTC/INR</p>
                <h2 className="mt-2 text-4xl font-bold text-white sm:text-5xl">
                  ₹98,50,000
                </h2>
                <p className="mt-2 text-sm text-gray-500">Bitcoin</p>
              </div>
              <span className="rounded-lg bg-green-400/10 px-3 py-2 text-sm font-semibold text-green-400">
                +2.41%
              </span>
            </div>

            <div className="flex h-72 items-end gap-2 rounded-xl border border-white/5 bg-black/10 px-3 pb-3 pt-5 sm:h-80 sm:gap-3 sm:px-4">
              {[40, 50, 45, 65, 58, 72, 68, 80, 75, 90, 84, 96].map(
                (height, index) => (
                  <div
                    key={index}
                    className="flex-1 rounded-t bg-blue-500/70 transition hover:bg-blue-400"
                    style={{ height: `${height}%` }}
                  />
                )
              )}
            </div>

            <div className="mt-5 grid grid-cols-2 gap-3">
              <Link
                href="/register"
                className="rounded-xl bg-green-500 py-4 text-center font-semibold text-white transition hover:bg-green-600"
              >
                Buy
              </Link>
              <Link
                href="/register"
                className="rounded-xl bg-red-500 py-4 text-center font-semibold text-white transition hover:bg-red-600"
              >
                Sell
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}