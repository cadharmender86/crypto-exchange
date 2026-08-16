"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { ApiError, login, saveTokens } from "@/lib/api";

const markets = [
  { symbol: "BTC/INR", price: "₹62,50,000", change: "+2.45%", tone: "text-emerald-400" },
  { symbol: "ETH/INR", price: "₹3,45,000", change: "+1.82%", tone: "text-emerald-400" },
  { symbol: "USDT/INR", price: "₹89.20", change: "+0.12%", tone: "text-emerald-400" },
];

function CoinIcon({ type }: { type: "btc" | "eth" | "usdt" }) {
  const styles = {
    btc: "bg-orange-500 text-white",
    eth: "bg-indigo-500 text-white",
    usdt: "bg-emerald-500 text-white",
  };
  const labels = { btc: "₿", eth: "◆", usdt: "₮" };

  return (
    <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-xl font-bold shadow-lg ${styles[type]}`}>
      {labels[type]}
    </span>
  );
}

function InputIcon({ type }: { type: "mail" | "lock" }) {
  return (
    <span className="text-blue-400" aria-hidden="true">
      {type === "mail" ? (
        <svg viewBox="0 0 24 24" className="h-5 w-5 fill-none stroke-current" strokeWidth="1.8">
          <rect x="3" y="5" width="18" height="14" rx="2" />
          <path d="m4 7 8 6 8-6" />
        </svg>
      ) : (
        <svg viewBox="0 0 24 24" className="h-5 w-5 fill-none stroke-current" strokeWidth="1.8">
          <rect x="5" y="10" width="14" height="10" rx="2" />
          <path d="M8 10V7a4 4 0 0 1 8 0v3" />
        </svg>
      )}
    </span>
  );
}

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const tokens = await login(email, password);
      saveTokens(tokens);
      window.location.href = "/dashboard";
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Unable to connect to BitNova API.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#020617] text-white">
      {/* Ambient exchange background */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -right-40 -top-44 h-[650px] w-[650px] rounded-full bg-blue-600/10 blur-3xl" />
        <div className="absolute -left-40 bottom-0 h-[500px] w-[700px] rounded-full bg-cyan-600/10 blur-3xl" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_15%,rgba(37,99,235,0.12),transparent_35%),linear-gradient(180deg,#020617_0%,#030b20_60%,#020617_100%)]" />
        <div className="absolute inset-x-0 bottom-0 h-64 opacity-20 [background-image:linear-gradient(rgba(37,99,235,.35)_1px,transparent_1px),linear-gradient(90deg,rgba(37,99,235,.35)_1px,transparent_1px)] [background-size:44px_44px] [mask-image:linear-gradient(to_top,black,transparent)]" />
      </div>

      <header className="relative z-10 border-b border-white/10 bg-[#020617]/75 backdrop-blur-xl">
        <div className="mx-auto flex h-[76px] max-w-[1450px] items-center justify-between px-5 sm:px-8 lg:px-12">
          <Link href="/" className="flex items-center gap-2.5">
            <span className="flex h-11 w-11 items-center justify-center text-4xl font-black italic leading-none text-blue-500">N</span>
            <span className="text-2xl font-bold tracking-tight">Bit<span className="text-blue-500">Nova</span></span>
          </Link>

          <nav className="hidden items-center gap-9 text-sm text-slate-300 lg:flex">
            <Link href="/" className="hover:text-white">Home</Link>
            <Link href="/markets" className="hover:text-white">Markets</Link>
            <Link href="/trade" className="hover:text-white">Trade</Link>
            <Link href="/wallet" className="hover:text-white">Wallet</Link>
            <Link href="/features" className="hover:text-white">Features</Link>
            <Link href="/support" className="hover:text-white">Support</Link>
          </nav>

          <div className="flex items-center gap-3 sm:gap-5">
            <button type="button" className="hidden text-lg text-slate-300 hover:text-white sm:block" aria-label="Toggle theme">☾</button>
            <span className="hidden h-6 w-px bg-white/10 sm:block" />
            <span className="hidden text-sm text-slate-300 sm:block">New to BitNova?</span>
            <Link href="/register" className="rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 px-4 py-2.5 text-sm font-semibold shadow-lg shadow-blue-600/20 hover:from-blue-400 hover:to-blue-500 sm:px-6">
              Create Account
            </Link>
          </div>
        </div>
      </header>

      <section className="relative z-10 mx-auto grid min-h-[calc(100vh-76px)] max-w-[1450px] items-center gap-8 px-5 py-8 sm:px-8 lg:grid-cols-[1fr_1.08fr] lg:gap-8 lg:px-12 lg:py-12">
        {/* Login panel */}
        <div className="relative overflow-hidden rounded-[28px] border border-blue-400/35 bg-[#06102a]/85 p-7 shadow-2xl shadow-blue-950/50 backdrop-blur-xl sm:p-10 lg:min-h-[700px] lg:p-12">
          <div className="absolute -top-20 left-1/2 h-40 w-72 -translate-x-1/2 rounded-full bg-blue-500/20 blur-3xl" />
          <div className="relative mx-auto max-w-xl">
            <div className="mb-9">
              <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">Welcome back <span aria-hidden="true">👋</span></h1>
              <p className="mt-3 text-lg text-slate-300">Trade crypto with confidence.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <label className="block">
                <span className="mb-2.5 block text-sm font-semibold text-slate-100">Email Address</span>
                <span className="flex items-center gap-3 rounded-xl border border-white/15 bg-[#08132c]/80 px-4 py-3.5 shadow-inner transition focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/15">
                  <InputIcon type="mail" />
                  <input
                    type="email"
                    required
                    autoComplete="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    className="min-w-0 flex-1 bg-transparent text-white outline-none placeholder:text-slate-500"
                    placeholder="Enter your email address"
                  />
                </span>
              </label>

              <label className="block">
                <span className="mb-2.5 block text-sm font-semibold text-slate-100">Password</span>
                <span className="flex items-center gap-3 rounded-xl border border-white/15 bg-[#08132c]/80 px-4 py-3.5 shadow-inner transition focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/15">
                  <InputIcon type="lock" />
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    autoComplete="current-password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    className="min-w-0 flex-1 bg-transparent text-white outline-none placeholder:text-slate-500"
                    placeholder="Enter your password"
                  />
                  <button type="button" onClick={() => setShowPassword((value) => !value)} className="text-slate-400 hover:text-white" aria-label={showPassword ? "Hide password" : "Show password"}>
                    {showPassword ? "◉" : "◌"}
                  </button>
                </span>
              </label>

              <div className="flex items-center justify-between gap-4 text-sm">
                <label className="flex cursor-pointer items-center gap-2.5 text-slate-200">
                  <input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} className="h-4 w-4 accent-blue-500" />
                  Remember me
                </label>
                <Link href="/forgot-password" className="font-medium text-blue-400 hover:text-blue-300">Forgot password?</Link>
              </div>

              {error && <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</div>}

              <button type="submit" disabled={loading} className="flex w-full items-center justify-center gap-3 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 py-4 text-lg font-bold shadow-xl shadow-blue-600/20 transition hover:from-blue-400 hover:to-blue-500 disabled:cursor-not-allowed disabled:opacity-60">
                {loading ? "Signing in..." : "Sign In"}
                {!loading && <span className="text-2xl leading-none">→</span>}
              </button>

              <div className="flex items-center gap-4 text-xs text-slate-500">
                <span className="h-px flex-1 bg-white/10" />
                <span>or</span>
                <span className="h-px flex-1 bg-white/10" />
              </div>

              <button type="button" className="flex w-full items-center justify-center gap-3 rounded-xl border border-white/15 bg-white/[0.02] py-3.5 font-semibold text-slate-200 hover:border-blue-400/50 hover:bg-white/[0.05]">
                <span className="text-lg font-bold">G</span>
                Continue with Google
              </button>
            </form>

            <div className="mt-7 flex items-start gap-3 rounded-xl border border-blue-500/15 bg-blue-500/[0.04] p-4">
              <span className="mt-0.5 text-xl text-blue-400">♢</span>
              <div>
                <p className="font-semibold text-slate-100">Secure Login</p>
                <p className="mt-1 text-xs leading-5 text-slate-400">Your account and personal data are protected with industry-standard security.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Market panel */}
        <div className="relative overflow-hidden rounded-[28px] border border-blue-400/25 bg-[#050d24]/75 p-7 shadow-2xl shadow-blue-950/50 backdrop-blur-xl sm:p-10 lg:min-h-[700px] lg:p-10">
          <div className="absolute -right-28 -top-24 h-72 w-72 rounded-full bg-blue-500/20 blur-3xl" />
          <div className="absolute -bottom-28 left-20 h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl" />

          <div className="relative">
            <div className="flex items-center justify-between border-b border-white/10 pb-5">
              <div className="flex items-center gap-3">
                <span className="h-3 w-3 rounded-full bg-emerald-400 shadow-lg shadow-emerald-400/60" />
                <h2 className="text-lg font-semibold tracking-wide">LIVE MARKET</h2>
              </div>
              <Link href="/markets" className="text-sm font-semibold text-blue-400 hover:text-blue-300">View All Markets →</Link>
            </div>

            <div className="mt-2 divide-y divide-white/10">
              {markets.map((market, index) => (
                <div key={market.symbol} className="flex items-center gap-4 py-5">
                  <CoinIcon type={index === 0 ? "btc" : index === 1 ? "eth" : "usdt"} />
                  <div className="min-w-0 flex-1">
                    <p className="text-lg font-semibold">{market.symbol}</p>
                    <p className="mt-0.5 text-2xl font-bold tracking-tight">{market.price}</p>
                  </div>
                  <span className={`rounded-lg border border-emerald-500/35 bg-emerald-500/10 px-3 py-2 text-sm font-semibold ${market.tone}`}>
                    ▲ {market.change.replace("+", "")}
                  </span>
                </div>
              ))}
            </div>

            <div className="relative mt-2 h-28 overflow-hidden rounded-xl border border-blue-500/10 bg-blue-500/[0.025]">
              <svg viewBox="0 0 700 150" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
                <defs>
                  <linearGradient id="marketGradient" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.25" />
                    <stop offset="100%" stopColor="#06b6d4" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <path d="M0 125 C35 128 40 100 70 112 S105 90 135 108 S165 70 195 92 S235 64 260 82 S300 42 330 70 S370 52 400 68 S440 38 470 60 S510 42 535 58 S570 35 600 48 S650 18 700 25 L700 150 L0 150 Z" fill="url(#marketGradient)" />
                <path d="M0 125 C35 128 40 100 70 112 S105 90 135 108 S165 70 195 92 S235 64 260 82 S300 42 330 70 S370 52 400 68 S440 38 470 60 S510 42 535 58 S570 35 600 48 S650 18 700 25" fill="none" stroke="#06b6d4" strokeWidth="4" />
              </svg>
            </div>

            <div className="mt-10 grid gap-6 sm:grid-cols-2">
              <div>
                <h2 className="text-3xl font-bold tracking-tight">Trade Smarter.</h2>
                <h2 className="mt-1 text-3xl font-bold tracking-tight text-blue-400">Move Faster.</h2>
                <p className="mt-4 max-w-md text-sm leading-6 text-slate-300">Buy, sell and manage digital assets securely with BitNova.</p>
              </div>
              <div className="hidden items-end justify-end sm:flex">
                <div className="relative h-32 w-40">
                  <div className="absolute bottom-2 left-10 h-24 w-24 rounded-full bg-orange-500 shadow-[0_0_45px_rgba(249,115,22,.35)]">
                    <span className="flex h-full items-center justify-center text-5xl font-bold text-white">₿</span>
                  </div>
                  <div className="absolute bottom-0 right-0 h-12 w-24 rounded-full bg-orange-700/80 shadow-lg" />
                </div>
              </div>
            </div>

            <div className="mt-7 grid grid-cols-3 gap-3 border-t border-white/10 pt-6 text-center text-xs text-slate-300">
              <div><span className="block text-lg text-emerald-400">✓</span>Secure & Reliable</div>
              <div><span className="block text-lg text-emerald-400">✓</span>INR Support</div>
              <div><span className="block text-lg text-emerald-400">✓</span>Fast Transactions</div>
            </div>
          </div>
        </div>
      </section>

      <footer className="relative z-10 border-t border-white/10 bg-[#020617]/80">
        <div className="mx-auto flex max-w-[1450px] flex-col items-center justify-between gap-4 px-5 py-5 text-xs text-slate-400 sm:flex-row sm:px-8 lg:px-12">
          <div className="flex items-center gap-3"><span className="text-xl font-black italic text-blue-500">N</span><span>© 2026 BitNova. All rights reserved.</span></div>
          <div className="flex gap-5"><Link href="/terms" className="hover:text-white">Terms</Link><Link href="/privacy" className="hover:text-white">Privacy</Link><Link href="/risk-disclosure" className="hover:text-white">Risk Disclosure</Link><Link href="/support" className="hover:text-white">Support</Link></div>
        </div>
      </footer>
    </main>
  );
}
