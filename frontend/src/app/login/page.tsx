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
    <span className="relative flex h-10 w-10 items-center justify-center text-3xl font-black italic leading-none text-cyan-400">
      N
      <span className="absolute inset-0 -z-10 rounded-xl bg-cyan-400/10 blur-md" />
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
    shield: <path d="M12 3 19 6v5c0 4.8-3 8.3-7 10-4-1.7-7-5.2-7-10V6l7-3Zm-3 9 2 2 4-5" />,
    bolt: <path d="m13 2-8 11h6l-1 9 8-12h-6l1-8Z" />,
    wallet: <path d="M4 6h15a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7a1 1 0 0 1 1-1h16M16 12h5" />,
    support: <><circle cx="12" cy="12" r="8" /><path d="M4 13H2v-2h2m16 2h2v-2h-2M8 18v2h8v-2" /></>,
  };

  return (
    <div className="flex min-w-0 flex-1 flex-col items-center text-center">
      <span className="mb-3 flex h-12 w-12 items-center justify-center rounded-full border border-cyan-400/20 bg-cyan-400/5 text-cyan-300 shadow-[0_0_25px_rgba(34,211,238,0.08)]">
        <svg viewBox="0 0 24 24" className="h-6 w-6 fill-none stroke-current" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{icons[type]}</svg>
      </span>
      <p className="text-sm font-semibold text-white">{title}</p>
      <p className="mt-1 max-w-[125px] text-[11px] leading-4 text-slate-400">{description}</p>
    </div>
  );
}

function MarketChart({ index }: { index: number }) {
  const paths = [
    "M0 58 C25 62 32 48 52 53 S75 40 92 48 S118 31 140 43 S166 20 185 35 S210 17 230 27 S255 12 280 22 S305 5 330 14 S350 8 370 4",
    "M0 56 C18 60 30 44 48 52 S72 36 90 44 S112 28 132 38 S158 25 176 31 S198 15 218 26 S245 9 265 20 S288 11 310 15 S340 2 370 7",
    "M0 55 C22 58 32 49 48 51 S70 35 88 42 S110 28 128 35 S150 21 168 30 S190 17 212 25 S238 10 256 18 S280 7 300 14 S332 5 370 2",
  ];

  return (
    <svg viewBox="0 0 370 65" preserveAspectRatio="none" className="h-16 w-full">
      <defs>
        <linearGradient id={`chart-${index}`} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.22" />
          <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={`${paths[index]} L370 65 L0 65 Z`} fill={`url(#chart-${index})`} />
      <path d={paths[index]} fill="none" stroke="#22d3ee" strokeWidth="2.5" />
    </svg>
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
    <main className="relative min-h-screen overflow-hidden bg-[#020617] text-white selection:bg-cyan-400/30">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-40 top-28 h-[560px] w-[560px] rounded-full bg-blue-700/10 blur-[110px]" />
        <div className="absolute right-[-180px] top-24 h-[700px] w-[700px] rounded-full bg-cyan-500/10 blur-[120px]" />
        <div className="absolute bottom-[-220px] left-[35%] h-[520px] w-[800px] rounded-full bg-blue-600/10 blur-[130px]" />
        <div className="absolute inset-0 opacity-30 [background-image:radial-gradient(circle_at_20%_20%,rgba(34,211,238,.12)_1px,transparent_1px),radial-gradient(circle_at_80%_65%,rgba(59,130,246,.12)_1px,transparent_1px)] [background-size:28px_28px,36px_36px]" />
      </div>

      <header className="relative z-20 border-b border-white/5 bg-[#020617]/80 backdrop-blur-xl">
        <div className="mx-auto flex h-[88px] max-w-[1480px] items-center justify-between px-5 sm:px-8 lg:px-12">
          <Link href="/" className="flex items-center gap-2.5">
            <BrandMark />
            <span className="text-[28px] font-bold tracking-tight">Bit<span className="text-cyan-400">Nova</span></span>
          </Link>

          <nav className="hidden items-center gap-10 text-[15px] font-medium text-slate-200 lg:flex">
            <Link href="/" className="transition hover:text-cyan-300">Home</Link>
            <Link href="/markets" className="transition hover:text-cyan-300">Markets</Link>
            <Link href="/trade" className="transition hover:text-cyan-300">Trade</Link>
            <Link href="/features" className="transition hover:text-cyan-300">Features</Link>
            <Link href="/fees" className="transition hover:text-cyan-300">Fees</Link>
            <Link href="/support" className="transition hover:text-cyan-300">Support</Link>
          </nav>

          <div className="flex items-center gap-4 sm:gap-6">
            <button type="button" className="hidden text-xl text-slate-300 transition hover:text-white sm:block" aria-label="Toggle theme">☾</button>
            <span className="hidden h-6 w-px bg-white/15 sm:block" />
            <span className="hidden text-sm text-slate-200 md:block">New to BitNova?</span>
            <Link href="/register" className="rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 px-4 py-3 text-sm font-bold shadow-lg shadow-blue-600/20 transition hover:from-blue-400 hover:to-cyan-400 sm:px-6">
              Create Account
            </Link>
          </div>
        </div>
      </header>

      <section className="relative z-10 mx-auto grid max-w-[1480px] gap-8 px-5 py-8 sm:px-8 lg:min-h-[calc(100vh-88px-72px)] lg:grid-cols-[minmax(0,0.94fr)_minmax(0,1.06fr)] lg:items-center lg:gap-10 lg:px-12 lg:py-10">
        <div className="relative overflow-hidden rounded-[26px] border border-blue-400/45 bg-[#04102a]/80 p-7 shadow-[0_0_70px_rgba(37,99,235,0.14)] backdrop-blur-xl sm:p-9 lg:p-10 xl:p-11">
          <div className="absolute -right-28 -top-28 h-72 w-72 rounded-full bg-blue-500/15 blur-3xl" />
          <div className="absolute -bottom-32 left-1/4 h-64 w-64 rounded-full bg-cyan-500/10 blur-3xl" />

          <div className="relative">
            <div className="mb-8">
              <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">Welcome back <span aria-hidden="true">👋</span></h1>
              <p className="mt-3 text-lg text-slate-300">Trade crypto with confidence.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <label className="block">
                <span className="mb-2.5 block text-sm font-semibold text-white">Email Address</span>
                <span className="flex h-[60px] items-center gap-4 rounded-xl border border-blue-200/20 bg-[#071534]/80 px-4 transition focus-within:border-cyan-400 focus-within:ring-2 focus-within:ring-cyan-400/10">
                  <InputIcon type="mail" />
                  <input type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} className="min-w-0 flex-1 bg-transparent text-white outline-none placeholder:text-slate-400" placeholder="Enter your email address" />
                </span>
              </label>

              <label className="block">
                <span className="mb-2.5 block text-sm font-semibold text-white">Password</span>
                <span className="flex h-[60px] items-center gap-4 rounded-xl border border-blue-200/20 bg-[#071534]/80 px-4 transition focus-within:border-cyan-400 focus-within:ring-2 focus-within:ring-cyan-400/10">
                  <InputIcon type="lock" />
                  <input type={showPassword ? "text" : "password"} required autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} className="min-w-0 flex-1 bg-transparent text-white outline-none placeholder:text-slate-400" placeholder="Enter your password" />
                  <button type="button" onClick={() => setShowPassword((value) => !value)} className="text-slate-400 transition hover:text-cyan-300" aria-label={showPassword ? "Hide password" : "Show password"}>
                    {showPassword ? "◉" : "◌"}
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

        <div className="relative min-w-0">
          <div className="pointer-events-none absolute -right-10 -top-20 h-72 w-72 rounded-full bg-blue-500/15 blur-3xl" />
          <div className="pointer-events-none absolute bottom-[-120px] right-[-80px] h-80 w-80 rounded-full bg-cyan-500/10 blur-3xl" />

          <div className="relative overflow-hidden rounded-[25px] border border-blue-300/25 bg-[#06112c]/75 p-6 shadow-2xl shadow-blue-950/40 backdrop-blur-xl sm:p-8">
            <div className="flex items-center justify-between border-b border-white/10 pb-5">
              <div className="flex items-center gap-3">
                <span className="h-3 w-3 rounded-full bg-emerald-400 shadow-[0_0_15px_rgba(52,211,153,.8)]" />
                <h2 className="text-lg font-bold tracking-wide">LIVE MARKET</h2>
              </div>
              <Link href="/markets" className="text-sm font-semibold text-cyan-300 hover:text-cyan-200">View All Markets →</Link>
            </div>

            <div className="divide-y divide-white/10">
              {markets.map((market, index) => (
                <div key={market.symbol} className="grid grid-cols-[auto_1fr_auto] items-center gap-4 py-5">
                  <span className={`flex h-11 w-11 items-center justify-center rounded-full ${market.iconClass} text-xl font-bold text-white shadow-lg`}>{market.icon}</span>
                  <div className="min-w-0">
                    <p className="text-base font-semibold text-slate-200">{market.symbol}</p>
                    <p className="mt-0.5 text-2xl font-bold tracking-tight text-white sm:text-[27px]">{market.price}</p>
                  </div>
                  <span className="rounded-lg border border-emerald-500/45 bg-emerald-500/10 px-3 py-2 text-sm font-semibold text-emerald-300">▲ {market.change.slice(1)}</span>
                  <div className="col-span-3 -mt-2 ml-[60px] opacity-95"><MarketChart index={index} /></div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-7 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <Benefit type="shield" title="Secure" description="Your assets protected" />
            <Benefit type="bolt" title="Fast" description="Quick transactions" />
            <Benefit type="wallet" title="INR Support" description="Deposit & withdraw INR" />
            <Benefit type="support" title="24/7 Support" description="Always here for you" />
          </div>

          <div className="relative mt-8 flex min-h-[170px] items-end overflow-hidden rounded-2xl px-2 sm:px-5">
            <div className="absolute inset-0 opacity-40 [background-image:linear-gradient(rgba(34,211,238,.16)_1px,transparent_1px),linear-gradient(90deg,rgba(34,211,238,.16)_1px,transparent_1px)] [background-size:34px_34px] [mask-image:linear-gradient(to_top,black,transparent)]" />
            <svg className="pointer-events-none absolute inset-0 h-full w-full" viewBox="0 0 800 230" preserveAspectRatio="none">
              <path d="M0 210 C90 200 120 145 210 170 S315 195 390 150 S510 120 590 140 S675 72 800 30" fill="none" stroke="#0ea5e9" strokeWidth="3" opacity=".75" />
              <path d="M0 230 C90 220 120 165 210 190 S315 215 390 170 S510 140 590 160 S675 92 800 50 L800 230 Z" fill="url(#heroGlow)" opacity=".22" />
              <defs><linearGradient id="heroGlow" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#22d3ee" /><stop offset="1" stopColor="#020617" stopOpacity="0" /></linearGradient></defs>
            </svg>
            <div className="relative z-10 pb-5">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Trade Smarter.</h2>
              <h2 className="mt-1 text-3xl font-bold tracking-tight text-cyan-400 sm:text-4xl">Move Faster.</h2>
              <p className="mt-3 text-sm text-slate-300">The trusted crypto exchange for India.</p>
            </div>
            <div className="pointer-events-none absolute -bottom-8 right-2 hidden h-44 w-56 sm:block">
              <div className="absolute bottom-0 right-8 h-28 w-28 rotate-12 rounded-full border-[14px] border-amber-400 bg-amber-500/10 shadow-[0_0_45px_rgba(245,158,11,.35)]" />
              <div className="absolute bottom-[-5px] right-[-5px] h-20 w-40 rounded-[50%] border-8 border-amber-500/80" />
              <div className="absolute bottom-[-10px] right-16 h-8 w-36 rounded-full bg-amber-500/30 blur-xl" />
            </div>
          </div>
        </div>
      </section>

      <footer className="relative z-20 border-t border-white/10 bg-[#020617]/90">
        <div className="mx-auto flex max-w-[1480px] flex-col items-center justify-between gap-3 px-5 py-4 text-xs text-slate-400 sm:flex-row sm:px-8 lg:px-12">
          <div className="flex items-center gap-3"><BrandMark /><span>© 2026 BitNova. All rights reserved.</span></div>
          <div className="flex flex-wrap justify-center gap-5"><Link href="/terms" className="hover:text-white">Terms</Link><Link href="/privacy" className="hover:text-white">Privacy</Link><Link href="/risk-disclosure" className="hover:text-white">Risk Disclosure</Link><Link href="/support" className="hover:text-white">Support</Link></div>
        </div>
      </footer>
    </main>
  );
}
