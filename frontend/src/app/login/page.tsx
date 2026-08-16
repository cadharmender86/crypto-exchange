"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { ApiError, login, saveTokens } from "@/lib/api";

const markets = [
  { symbol: "BTC/INR", price: "₹62,50,000", change: "+2.45%", icon: "₿", iconClass: "bg-orange-500" },
  { symbol: "ETH/INR", price: "₹3,45,000", change: "+1.82%", icon: "◆", iconClass: "bg-indigo-500" },
  { symbol: "USDT/INR", price: "₹89.20", change: "+0.12%", icon: "₮", iconClass: "bg-emerald-500" },
];

function BrandMark() {
  return (
    <span className="relative flex h-11 w-11 items-center justify-center" aria-hidden="true">
      <svg viewBox="0 0 48 48" className="h-11 w-11">
        <defs>
          <linearGradient id="brandGradient" x1="4" y1="4" x2="44" y2="44">
            <stop offset="0%" stopColor="#22d3ee" />
            <stop offset="100%" stopColor="#1677ff" />
          </linearGradient>
        </defs>
        <path d="M8 4 24 14 40 4v15L24 29 8 19V4Z" fill="url(#brandGradient)" />
        <path d="M8 24 24 34 40 24v15L24 48 8 39V24Z" fill="url(#brandGradient)" opacity=".92" />
        <path d="M24 14v20" stroke="#06112c" strokeWidth="3" opacity=".8" />
      </svg>
    </span>
  );
}

function InputIcon({ type }: { type: "mail" | "lock" }) {
  return (
    <span className="text-cyan-300" aria-hidden="true">
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

function Benefit({ type, title, description }: { type: "shield" | "bolt" | "wallet" | "support"; title: string; description: string }) {
  const icons = {
    shield: <><path d="M12 3 19 6v5c0 4.8-3 8.3-7 10-4-1.7-7-5.2-7-10V6l7-3Z" /><path d="m9 12 2 2 4-5" /></>,
    bolt: <path d="m13 2-8 11h6l-1 9 8-12h-6l1-8Z" />,
    wallet: <><rect x="3" y="6" width="18" height="14" rx="2" /><path d="M16 12h5M7 6V4h11a2 2 0 0 1 2 2" /></>,
    support: <><circle cx="12" cy="12" r="8" /><path d="M4 13H2v-2h2m16 2h2v-2h-2M8 18v2h8v-2" /></>,
  };

  return (
    <div className="flex min-w-0 flex-1 flex-col items-center text-center">
      <span className="mb-3 flex h-12 w-12 items-center justify-center rounded-full border border-cyan-400/25 bg-[#041a32] text-cyan-300 shadow-[0_0_25px_rgba(34,211,238,0.08)]">
        <svg viewBox="0 0 24 24" className="h-6 w-6 fill-none stroke-current" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{icons[type]}</svg>
      </span>
      <p className="text-sm font-semibold text-white">{title}</p>
      <p className="mt-1 max-w-[130px] text-[11px] leading-4 text-slate-400">{description}</p>
    </div>
  );
}

function MarketChart({ index }: { index: number }) {
  const paths = [
    "M0 45 C28 48 38 42 58 44 S88 36 106 40 S132 31 151 36 S176 27 198 31 S223 20 244 25 S270 19 291 22 S320 13 342 17 S356 11 370 8",
    "M0 48 C26 51 39 43 60 46 S86 35 107 39 S132 29 151 34 S178 25 198 29 S221 20 244 23 S270 16 291 19 S321 11 343 14 S357 9 370 7",
    "M0 47 C22 50 39 44 59 46 S84 38 105 41 S128 31 148 35 S174 27 195 30 S222 21 242 24 S269 16 291 20 S317 12 340 16 S357 10 370 6",
  ];

  return (
    <svg viewBox="0 0 370 65" preserveAspectRatio="none" className="h-[70px] w-full">
      <defs>
        <linearGradient id={`chartFill-${index}`} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.20" />
          <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={`${paths[index]} L370 65 L0 65 Z`} fill={`url(#chartFill-${index})`} />
      <path d={paths[index]} fill="none" stroke="#22d3ee" strokeWidth="2.5" />
    </svg>
  );
}

function CryptoDecoration() {
  return (
    <div className="pointer-events-none absolute bottom-[-18px] right-[-10px] h-[230px] w-[430px] opacity-80" aria-hidden="true">
      <div className="absolute bottom-4 right-5 h-40 w-40 rounded-full border border-blue-500/25 bg-gradient-to-br from-blue-400/15 to-blue-950/40 shadow-[0_0_60px_rgba(37,99,235,.18)]" />
      <div className="absolute bottom-0 right-20 h-20 w-52 rounded-[50%] border-t-2 border-cyan-400/50 bg-blue-500/10 blur-[1px]" />
      <div className="absolute bottom-8 left-8 h-20 w-52 rotate-[-12deg] rounded-[50%] border-t-2 border-orange-400/50" />
      <div className="absolute bottom-2 left-24 h-12 w-28 rounded-full bg-orange-500/10 blur-xl" />
      <svg viewBox="0 0 430 230" className="absolute inset-0 h-full w-full">
        <path d="M0 204 C45 190 60 203 94 183 S138 174 169 186 S209 164 235 171 S269 144 295 157 S331 122 351 135 S385 94 430 75" fill="none" stroke="#f59e0b" strokeWidth="2" opacity=".55" />
        <path d="M0 220 C55 204 73 215 108 198 S151 190 183 200 S225 182 250 187 S284 165 311 177 S350 148 370 159 S401 125 430 112" fill="none" stroke="#22d3ee" strokeWidth="2" opacity=".35" />
      </svg>
    </div>
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
      setError(err instanceof ApiError ? err.message : "Unable to connect to BitNova API.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative min-h-screen overflow-x-hidden bg-[#020617] text-white selection:bg-cyan-400/30">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-48 top-20 h-[620px] w-[620px] rounded-full bg-blue-700/10 blur-[120px]" />
        <div className="absolute right-[-220px] top-10 h-[760px] w-[760px] rounded-full bg-cyan-500/10 blur-[130px]" />
        <div className="absolute bottom-[-260px] left-[30%] h-[600px] w-[900px] rounded-full bg-blue-600/10 blur-[140px]" />
        <div className="absolute inset-0 opacity-35 [background-image:radial-gradient(circle_at_12%_24%,rgba(34,211,238,.13)_1px,transparent_1px),radial-gradient(circle_at_76%_72%,rgba(59,130,246,.11)_1px,transparent_1px)] [background-size:30px_30px,38px_38px]" />
      </div>

      <header className="relative z-20 h-[88px] border-b border-white/5 bg-[#020617]/85 backdrop-blur-xl">
        <div className="mx-auto flex h-full max-w-[1430px] items-center justify-between px-5 sm:px-8 lg:px-10">
          <Link href="/" className="flex items-center gap-2.5">
            <BrandMark />
            <span className="text-[28px] font-bold tracking-tight">Bit<span className="text-cyan-400">Nova</span></span>
          </Link>

          <nav className="hidden items-center gap-9 text-[15px] font-medium text-slate-200 lg:flex">
            <Link href="/" className="transition hover:text-cyan-300">Home</Link>
            <Link href="/markets" className="transition hover:text-cyan-300">Markets</Link>
            <Link href="/trade" className="transition hover:text-cyan-300">Trade</Link>
            <Link href="/features" className="transition hover:text-cyan-300">Features</Link>
            <Link href="/fees" className="transition hover:text-cyan-300">Fees</Link>
            <Link href="/support" className="transition hover:text-cyan-300">Support</Link>
          </nav>

          <div className="flex items-center gap-4 sm:gap-6">
            <button type="button" className="hidden text-lg text-slate-300 transition hover:text-white sm:block" aria-label="Toggle theme">☾</button>
            <span className="hidden h-6 w-px bg-white/15 sm:block" />
            <span className="hidden text-sm text-slate-200 md:block">New to BitNova?</span>
            <Link href="/register" className="rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 px-4 py-2.5 text-sm font-bold shadow-lg shadow-blue-600/20 transition hover:from-blue-400 hover:to-cyan-400 sm:px-6">
              Create Account
            </Link>
          </div>
        </div>
      </header>

      <section className="relative z-10 mx-auto grid max-w-[1330px] gap-8 px-5 py-8 sm:px-8 lg:min-h-[calc(100vh-88px-74px)] lg:grid-cols-[590px_1fr] lg:items-start lg:gap-[35px] lg:px-0 lg:pt-[62px]">
        <div className="relative min-h-[754px] overflow-hidden rounded-[26px] border border-blue-400/45 bg-[#04102a]/90 p-7 shadow-[0_0_70px_rgba(37,99,235,0.16)] backdrop-blur-xl sm:p-9 lg:p-10 xl:p-11">
          <div className="absolute -right-32 -top-32 h-80 w-80 rounded-full bg-blue-500/15 blur-3xl" />
          <div className="absolute -bottom-40 left-1/4 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl" />

          <div className="relative">
            <div className="mb-8">
              <h1 className="text-[38px] font-bold leading-tight tracking-tight sm:text-[42px]">Welcome back <span aria-hidden="true">👋</span></h1>
              <p className="mt-2 text-[17px] text-slate-300">Trade crypto with confidence.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <label className="block">
                <span className="mb-2.5 block text-sm font-semibold text-white">Email Address</span>
                <span className="flex h-[60px] items-center gap-4 rounded-xl border border-blue-200/20 bg-[#071534]/90 px-4 transition focus-within:border-cyan-400 focus-within:ring-2 focus-within:ring-cyan-400/10">
                  <InputIcon type="mail" />
                  <input type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} className="min-w-0 flex-1 bg-transparent text-white outline-none placeholder:text-slate-400" placeholder="Enter your email address" />
                </span>
              </label>

              <label className="block">
                <span className="mb-2.5 block text-sm font-semibold text-white">Password</span>
                <span className="flex h-[60px] items-center gap-4 rounded-xl border border-blue-200/20 bg-[#071534]/90 px-4 transition focus-within:border-cyan-400 focus-within:ring-2 focus-within:ring-cyan-400/10">
                  <InputIcon type="lock" />
                  <input type={showPassword ? "text" : "password"} required autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} className="min-w-0 flex-1 bg-transparent text-white outline-none placeholder:text-slate-400" placeholder="Enter your password" />
                  <button type="button" onClick={() => setShowPassword((value) => !value)} className="text-slate-400 transition hover:text-cyan-300" aria-label={showPassword ? "Hide password" : "Show password"}>
                    <svg viewBox="0 0 24 24" className="h-5 w-5 fill-none stroke-current" strokeWidth="1.8">
                      <path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" />
                      <circle cx="12" cy="12" r="2.5" />
                      {showPassword && <path d="m4 4 16 16" />}
                    </svg>
                  </button>
                </span>
              </label>

              <div className="flex items-center justify-between gap-4 pt-1 text-sm">
                <label className="flex cursor-pointer items-center gap-2.5 text-slate-200">
                  <input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} className="h-5 w-5 accent-cyan-400" />
                  Remember me
                </label>
                <Link href="/forgot-password" className="font-medium text-cyan-300 transition hover:text-cyan-200">Forgot password?</Link>
              </div>

              {error && <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</div>}

              <button type="submit" disabled={loading} className="flex h-[58px] w-full items-center justify-center gap-3 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 text-lg font-bold shadow-xl shadow-blue-600/20 transition hover:from-blue-500 hover:to-cyan-400 disabled:cursor-not-allowed disabled:opacity-60">
                {loading ? "Signing in..." : "Sign In"}
                {!loading && <span className="text-2xl leading-none">→</span>}
              </button>

              <div className="flex items-center gap-4 py-1 text-sm text-slate-400">
                <span className="h-px flex-1 bg-white/15" />
                <span>or</span>
                <span className="h-px flex-1 bg-white/15" />
              </div>

              <button type="button" className="flex h-[56px] w-full items-center justify-center gap-3 rounded-xl border border-cyan-400/45 bg-transparent font-semibold text-white transition hover:bg-cyan-400/5">
                <span className="text-xl font-bold text-white">G</span>
                Continue with Google
              </button>
            </form>

            <div className="mt-6 flex items-start gap-4 text-sm">
              <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-cyan-400/30 bg-cyan-400/5 text-cyan-300">✓</span>
              <div>
                <p className="font-semibold text-white">Secure Login</p>
                <p className="mt-1 text-xs leading-5 text-slate-400">Your data is protected with bank-grade encryption.</p>
              </div>
            </div>
          </div>
        </div>

        <div className="relative min-w-0 lg:pt-3">
          <div className="pointer-events-none absolute -right-24 -top-20 h-80 w-80 rounded-full bg-blue-500/15 blur-3xl" />
          <div className="pointer-events-none absolute right-[-120px] top-[70px] h-[470px] w-[470px] rounded-full border border-blue-500/10 bg-[radial-gradient(circle_at_35%_30%,rgba(37,99,235,.18),transparent_48%)]" />

          <div className="relative overflow-hidden rounded-[25px] border border-blue-300/25 bg-[#06112c]/80 p-6 shadow-2xl shadow-blue-950/40 backdrop-blur-xl sm:p-7">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <div className="flex items-center gap-3">
                <span className="h-3 w-3 rounded-full bg-emerald-400 shadow-[0_0_14px_rgba(52,211,153,.8)]" />
                <h2 className="text-[17px] font-bold tracking-wide">LIVE MARKET</h2>
              </div>
              <Link href="/markets" className="text-sm font-semibold text-cyan-300 hover:text-cyan-200">View All Markets →</Link>
            </div>

            <div className="divide-y divide-white/10">
              {markets.map((market, index) => (
                <div key={market.symbol} className="pt-4 first:pt-3 last:pb-1">
                  <div className="flex items-center gap-3">
                    <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${market.iconClass} text-lg font-bold text-white shadow-lg`}>{market.icon}</span>
                    <div className="min-w-0 flex-1">
                      <p className="text-[15px] font-semibold text-slate-200">{market.symbol}</p>
                      <p className="text-[25px] font-bold leading-8 tracking-tight">{market.price}</p>
                    </div>
                    <span className="rounded-lg border border-emerald-500/45 bg-emerald-500/10 px-3 py-1.5 text-sm font-semibold text-emerald-300">▲ {market.change.replace("+", "")}</span>
                  </div>
                  <div className="mt-1 pl-[58px]"><MarketChart index={index} /></div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative mt-5 grid grid-cols-4 gap-2">
            <Benefit type="shield" title="Secure" description="Your assets protected" />
            <Benefit type="bolt" title="Fast" description="Quick transactions" />
            <Benefit type="wallet" title="INR Support" description="Deposit & withdraw INR" />
            <Benefit type="support" title="24/7 Support" description="Always here for you" />
          </div>

          <div className="relative mt-9 min-h-[150px] overflow-hidden px-1 sm:px-2">
            <h2 className="text-[31px] font-bold leading-tight">Trade Smarter.</h2>
            <h2 className="text-[31px] font-bold leading-tight text-cyan-400">Move Faster.</h2>
            <p className="mt-2 max-w-[350px] text-sm leading-6 text-slate-200">The trusted crypto exchange for India.</p>
            <CryptoDecoration />
          </div>
        </div>
      </section>

      <footer className="relative z-20 border-t border-white/10 bg-[#020617]/90">
        <div className="mx-auto flex min-h-[74px] max-w-[1430px] flex-col items-center justify-between gap-3 px-5 py-4 text-xs text-slate-400 sm:flex-row sm:px-8 lg:px-0">
          <div className="flex items-center gap-3"><BrandMark /><span>© 2026 BitNova. All rights reserved.</span></div>
          <div className="flex flex-wrap justify-center gap-5"><Link href="/terms" className="hover:text-white">Terms</Link><span>|</span><Link href="/privacy" className="hover:text-white">Privacy</Link><span>|</span><Link href="/risk-disclosure" className="hover:text-white">Risk Disclosure</Link><span>|</span><Link href="/support" className="hover:text-white">Support</Link></div>
        </div>
      </footer>
    </main>
  );
}
