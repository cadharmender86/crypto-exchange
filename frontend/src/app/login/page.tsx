"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { ApiError, login, saveTokens } from "@/lib/api";

const markets = [
  { symbol: "BTC/INR", price: "₹62,50,000", change: "+2.45%", icon: "₿", iconClass: "bg-orange-500", glow: "rgba(249,115,22,.35)" },
  { symbol: "ETH/INR", price: "₹3,45,000", change: "+1.82%", icon: "◆", iconClass: "bg-indigo-500", glow: "rgba(99,102,241,.35)" },
  { symbol: "USDT/INR", price: "₹89.20", change: "+0.12%", icon: "₮", iconClass: "bg-emerald-500", glow: "rgba(16,185,129,.35)" },
];

function BrandMark() {
  return (
    <span className="relative flex h-11 w-11 items-center justify-center" aria-hidden="true">
      <span className="absolute inset-1 rounded-xl bg-cyan-400/10 blur-md" />
      <svg viewBox="0 0 48 48" className="relative h-11 w-11 drop-shadow-[0_0_12px_rgba(34,211,238,.35)]">
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

function Icon({ name, className = "h-5 w-5" }: { name: "mail" | "lock" | "eye" | "shield" | "bolt" | "wallet" | "support"; className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={`${className} fill-none stroke-current`} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {name === "mail" && <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m4 7 8 6 8-6" /></>}
      {name === "lock" && <><rect x="5" y="10" width="14" height="10" rx="2" /><path d="M8 10V7a4 4 0 0 1 8 0v3" /></>}
      {name === "eye" && <><path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" /><circle cx="12" cy="12" r="2.5" /></>}
      {name === "shield" && <><path d="M12 3 19 6v5c0 4.8-3 8.3-7 10-4-1.7-7-5.2-7-10V6l7-3Z" /><path d="m9 12 2 2 4-5" /></>}
      {name === "bolt" && <path d="m13 2-8 11h6l-1 9 8-12h-6l1-8Z" />}
      {name === "wallet" && <><rect x="3" y="6" width="18" height="14" rx="2" /><path d="M16 12h5M7 6V4h11a2 2 0 0 1 2 2" /></>}
      {name === "support" && <><circle cx="12" cy="12" r="8" /><path d="M4 13H2v-2h2m16 2h2v-2h-2M8 18v2h8v-2" /></>}
    </svg>
  );
}

function MarketChart({ index }: { index: number }) {
  const paths = [
    "M0 45 C28 48 38 42 58 44 S88 36 106 40 S132 31 151 36 S176 27 198 31 S223 20 244 25 S270 19 291 22 S320 13 342 17 S356 11 370 8",
    "M0 48 C26 51 39 43 60 46 S86 35 107 39 S132 29 151 34 S178 25 198 29 S221 20 244 23 S270 16 291 19 S321 11 343 14 S357 9 370 7",
    "M0 47 C22 50 39 44 59 46 S84 38 105 41 S128 31 148 35 S174 27 195 30 S222 21 242 24 S269 16 291 20 S317 12 340 16 S357 10 370 6",
  ];
  return (
    <svg viewBox="0 0 370 65" preserveAspectRatio="none" className="h-[72px] w-full">
      <defs>
        <linearGradient id={`chartFill-${index}`} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#22d3ee" stopOpacity=".24" />
          <stop offset="100%" stopColor="#22d3ee" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={`${paths[index]} L370 65 L0 65 Z`} fill={`url(#chartFill-${index})`} />
      <path d={paths[index]} fill="none" stroke="#22d3ee" strokeWidth="2.7" />
    </svg>
  );
}

function Benefit({ icon, title, description }: { icon: "shield" | "bolt" | "wallet" | "support"; title: string; description: string }) {
  return (
    <div className="group flex min-w-0 flex-1 flex-col items-center text-center transition duration-300 hover:-translate-y-1">
      <span className="mb-3 flex h-12 w-12 items-center justify-center rounded-full border border-cyan-400/25 bg-[#041a32]/90 text-cyan-300 shadow-[0_0_25px_rgba(34,211,238,.08)] transition group-hover:border-cyan-300/50 group-hover:shadow-[0_0_30px_rgba(34,211,238,.16)]">
        <Icon name={icon} className="h-6 w-6" />
      </span>
      <p className="text-sm font-semibold text-white">{title}</p>
      <p className="mt-1 max-w-[130px] text-[11px] leading-4 text-slate-400">{description}</p>
    </div>
  );
}

function CryptoDecoration() {
  return (
    <div className="pointer-events-none absolute bottom-[-8px] right-[-10px] h-[230px] w-[430px] opacity-90" aria-hidden="true">
      <div className="absolute bottom-3 right-6 h-40 w-40 rounded-full border border-blue-500/25 bg-gradient-to-br from-blue-400/15 to-blue-950/50 shadow-[0_0_70px_rgba(37,99,235,.22)]" />
      <div className="absolute bottom-[-8px] right-20 h-24 w-56 rounded-[50%] border-t-2 border-cyan-400/50 bg-cyan-400/5 blur-[1px]" />
      <div className="absolute bottom-8 left-8 h-20 w-52 rotate-[-12deg] rounded-[50%] border-t-2 border-orange-400/55" />
      <div className="absolute bottom-1 left-24 h-14 w-32 rounded-full bg-orange-500/15 blur-xl" />
      <svg viewBox="0 0 430 230" className="absolute inset-0 h-full w-full">
        <path d="M0 204 C45 190 60 203 94 183 S138 174 169 186 S209 164 235 171 S269 144 295 157 S331 122 351 135 S385 94 430 75" fill="none" stroke="#f59e0b" strokeWidth="2" opacity=".62" />
        <path d="M0 220 C55 204 73 215 108 198 S151 190 183 200 S225 182 250 187 S284 165 311 177 S350 148 370 159 S401 125 430 112" fill="none" stroke="#22d3ee" strokeWidth="2" opacity=".42" />
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
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-52 top-10 h-[680px] w-[680px] rounded-full bg-blue-700/12 blur-[130px]" />
        <div className="absolute right-[-240px] top-0 h-[780px] w-[780px] rounded-full bg-cyan-500/10 blur-[140px]" />
        <div className="absolute bottom-[-300px] left-[30%] h-[650px] w-[950px] rounded-full bg-blue-600/10 blur-[150px]" />
        <div className="absolute inset-0 opacity-30 [background-image:radial-gradient(circle_at_15%_22%,rgba(34,211,238,.16)_1px,transparent_1px),radial-gradient(circle_at_78%_72%,rgba(59,130,246,.12)_1px,transparent_1px)] [background-size:30px_30px,42px_42px]" />
      </div>

      <header className="relative z-30 h-[88px] border-b border-white/5 bg-[#020617]/90 shadow-[0_10px_40px_rgba(0,0,0,.22)] backdrop-blur-2xl">
        <div className="mx-auto flex h-full max-w-[1430px] items-center justify-between px-5 sm:px-8 lg:px-10">
          <Link href="/" className="group flex items-center gap-2.5">
            <BrandMark />
            <span className="text-[28px] font-bold tracking-tight">Bit<span className="text-cyan-400">Nova</span></span>
          </Link>

          <nav className="hidden items-center gap-9 text-[15px] font-medium text-slate-200 lg:flex">
            {[["/", "Home"], ["/markets", "Markets"], ["/trade", "Trade"], ["/features", "Features"], ["/fees", "Fees"], ["/support", "Support"]].map(([href, label]) => (
              <Link key={href} href={href} className="relative py-2 transition hover:text-cyan-300">
                {label}
                <span className="absolute inset-x-0 bottom-0 h-px origin-left scale-x-0 bg-cyan-400 transition-transform duration-300 hover:scale-x-100" />
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-4 sm:gap-6">
            <button type="button" className="hidden text-lg text-slate-300 transition hover:text-cyan-300 sm:block" aria-label="Toggle theme">☾</button>
            <span className="hidden h-6 w-px bg-white/15 sm:block" />
            <span className="hidden text-sm text-slate-200 md:block">New to BitNova?</span>
            <Link href="/register" className="rounded-xl bg-gradient-to-r from-blue-500 via-blue-500 to-cyan-500 px-4 py-2.5 text-sm font-bold shadow-[0_8px_30px_rgba(37,99,235,.28)] transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_12px_35px_rgba(34,211,238,.22)] sm:px-6">Create Account</Link>
          </div>
        </div>
      </header>

      <section className="relative z-10 mx-auto grid max-w-[1330px] gap-8 px-5 py-8 sm:px-8 lg:min-h-[calc(100vh-88px-74px)] lg:grid-cols-[590px_1fr] lg:items-start lg:gap-[35px] lg:px-0 lg:pt-[58px]">
        <div className="group relative min-h-[754px] overflow-hidden rounded-[28px] border border-blue-400/50 bg-[linear-gradient(145deg,rgba(7,23,57,.97),rgba(3,12,34,.97))] p-7 shadow-[0_0_90px_rgba(37,99,235,.15),inset_0_1px_0_rgba(255,255,255,.04)] backdrop-blur-xl sm:p-9 lg:p-10 xl:p-11">
          <div className="absolute inset-x-12 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/70 to-transparent" />
          <div className="absolute -right-36 -top-36 h-96 w-96 rounded-full bg-blue-500/15 blur-3xl transition duration-700 group-hover:bg-blue-500/20" />
          <div className="absolute -bottom-40 left-1/4 h-80 w-80 rounded-full bg-cyan-500/10 blur-3xl" />
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,.025)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.025)_1px,transparent_1px)] [background-size:42px_42px] opacity-20" />

          <div className="relative">
            <div className="mb-8">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/5 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[.16em] text-cyan-300">
                <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_10px_rgba(34,211,238,.8)]" /> Secure access
              </div>
              <h1 className="text-[38px] font-bold leading-tight tracking-tight sm:text-[42px]">Welcome back <span aria-hidden="true">👋</span></h1>
              <p className="mt-2 text-[17px] text-slate-300">Trade crypto with confidence.</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <label className="block">
                <span className="mb-2.5 block text-sm font-semibold text-white">Email Address</span>
                <span className="flex h-[60px] items-center gap-4 rounded-xl border border-blue-200/20 bg-[#071534]/90 px-4 shadow-[inset_0_1px_0_rgba(255,255,255,.025)] transition duration-300 focus-within:border-cyan-400/70 focus-within:bg-[#081a3b] focus-within:shadow-[0_0_28px_rgba(34,211,238,.08)]">
                  <span className="text-cyan-300"><Icon name="mail" /></span>
                  <input type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} className="min-w-0 flex-1 bg-transparent text-white outline-none placeholder:text-slate-500" placeholder="Enter your email address" />
                </span>
              </label>

              <label className="block">
                <span className="mb-2.5 block text-sm font-semibold text-white">Password</span>
                <span className="flex h-[60px] items-center gap-4 rounded-xl border border-blue-200/20 bg-[#071534]/90 px-4 shadow-[inset_0_1px_0_rgba(255,255,255,.025)] transition duration-300 focus-within:border-cyan-400/70 focus-within:bg-[#081a3b] focus-within:shadow-[0_0_28px_rgba(34,211,238,.08)]">
                  <span className="text-cyan-300"><Icon name="lock" /></span>
                  <input type={showPassword ? "text" : "password"} required autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} className="min-w-0 flex-1 bg-transparent text-white outline-none placeholder:text-slate-500" placeholder="Enter your password" />
                  <button type="button" onClick={() => setShowPassword((value) => !value)} className="text-slate-500 transition hover:text-cyan-300" aria-label={showPassword ? "Hide password" : "Show password"}>
                    <Icon name="eye" />
                  </button>
                </span>
              </label>

              <div className="flex items-center justify-between gap-4 pt-1 text-sm">
                <label className="flex cursor-pointer items-center gap-2.5 text-slate-200">
                  <input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} className="h-4 w-4 accent-cyan-400" /> Remember me
                </label>
                <Link href="/forgot-password" className="font-medium text-cyan-300 transition hover:text-cyan-200">Forgot password?</Link>
              </div>

              {error && <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</div>}

              <button type="submit" disabled={loading} className="group/btn relative flex h-[58px] w-full items-center justify-center gap-3 overflow-hidden rounded-xl bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 text-lg font-bold shadow-[0_10px_35px_rgba(37,99,235,.26)] transition duration-300 hover:-translate-y-0.5 hover:shadow-[0_14px_42px_rgba(34,211,238,.22)] disabled:cursor-not-allowed disabled:opacity-60">
                <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform duration-700 group-hover/btn:translate-x-full" />
                <span className="relative">{loading ? "Signing in..." : "Sign In"}</span>
                {!loading && <span className="relative text-2xl leading-none transition-transform duration-300 group-hover/btn:translate-x-1">→</span>}
              </button>

              <div className="flex items-center gap-4 py-1 text-sm text-slate-500"><span className="h-px flex-1 bg-white/10" /><span>or</span><span className="h-px flex-1 bg-white/10" /></div>

              <button type="button" className="group/google flex h-[56px] w-full items-center justify-center gap-3 rounded-xl border border-cyan-400/35 bg-white/[.015] font-semibold text-white transition duration-300 hover:border-cyan-300/60 hover:bg-cyan-400/5">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-white text-sm font-black text-[#4285F4] transition-transform group-hover/google:scale-105">G</span>
                Continue with Google
              </button>
            </form>

            <div className="mt-7 flex items-start gap-4 rounded-2xl border border-white/5 bg-white/[.018] p-4">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-cyan-400/25 bg-cyan-400/5 text-cyan-300"><Icon name="shield" /></span>
              <div><p className="font-semibold text-white">Secure Login</p><p className="mt-1 text-xs leading-5 text-slate-400">Your data is protected with bank-grade encryption.</p></div>
              <span className="ml-auto mt-1 hidden rounded-full border border-emerald-400/20 bg-emerald-400/5 px-2 py-1 text-[10px] font-semibold text-emerald-300 sm:block">PROTECTED</span>
            </div>
          </div>
        </div>

        <div className="relative min-w-0 lg:pt-3">
          <div className="pointer-events-none absolute -right-24 -top-20 h-80 w-80 rounded-full bg-blue-500/15 blur-3xl" />
          <div className="pointer-events-none absolute right-[-130px] top-[50px] h-[520px] w-[520px] rounded-full border border-blue-500/10 bg-[radial-gradient(circle_at_35%_30%,rgba(37,99,235,.20),transparent_50%)]" />

          <div className="relative overflow-hidden rounded-[26px] border border-blue-300/30 bg-[linear-gradient(145deg,rgba(6,20,49,.94),rgba(3,13,35,.92))] p-6 shadow-[0_20px_70px_rgba(2,6,23,.55),0_0_55px_rgba(37,99,235,.08)] backdrop-blur-xl sm:p-7">
            <div className="absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/50 to-transparent" />
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <div className="flex items-center gap-3"><span className="h-3 w-3 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_16px_rgba(52,211,153,.9)]" /><h2 className="text-[17px] font-bold tracking-wide">LIVE MARKET</h2></div>
              <Link href="/markets" className="text-sm font-semibold text-cyan-300 transition hover:text-cyan-100">View All Markets →</Link>
            </div>

            <div className="divide-y divide-white/10">
              {markets.map((market, index) => (
                <div key={market.symbol} className="group/market py-4 first:pt-4 last:pb-1">
                  <div className="flex items-center gap-3">
                    <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${market.iconClass} text-lg font-bold text-white shadow-[0_0_25px_${market.glow}] transition duration-300 group-hover/market:scale-105`}>{market.icon}</span>
                    <div className="min-w-0 flex-1"><p className="text-[14px] font-semibold text-slate-300">{market.symbol}</p><p className="text-[26px] font-bold leading-8 tracking-tight">{market.price}</p></div>
                    <span className="rounded-lg border border-emerald-500/45 bg-emerald-500/10 px-3 py-1.5 text-xs font-bold text-emerald-300 shadow-[0_0_18px_rgba(16,185,129,.06)]">▲ {market.change.replace("+", "")}</span>
                  </div>
                  <div className="mt-1 pl-[58px]"><MarketChart index={index} /></div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative mt-5 grid grid-cols-4 gap-2 rounded-2xl border border-white/5 bg-white/[.012] px-2 py-4">
            <Benefit icon="shield" title="Secure" description="Your assets protected" />
            <Benefit icon="bolt" title="Fast" description="Quick transactions" />
            <Benefit icon="wallet" title="INR Support" description="Deposit & withdraw INR" />
            <Benefit icon="support" title="24/7 Support" description="Always here for you" />
          </div>

          <div className="relative mt-8 min-h-[170px] overflow-hidden rounded-2xl border border-white/5 bg-gradient-to-r from-transparent via-blue-500/[.035] to-cyan-500/[.04] px-2 py-5">
            <div className="relative z-10">
              <div className="mb-2 inline-flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.2em] text-cyan-300"><span className="h-1.5 w-1.5 rounded-full bg-cyan-300" /> Built for India</div>
              <h2 className="text-[31px] font-bold leading-tight">Trade Smarter.</h2>
              <h2 className="text-[31px] font-bold leading-tight text-cyan-400">Move Faster.</h2>
              <p className="mt-2 max-w-[360px] text-sm leading-6 text-slate-300">The trusted crypto exchange experience for secure INR trading.</p>
            </div>
            <CryptoDecoration />
          </div>
        </div>
      </section>

      <footer className="relative z-20 border-t border-white/10 bg-[#020617]/95">
        <div className="mx-auto flex min-h-[74px] max-w-[1430px] flex-col items-center justify-between gap-3 px-5 py-4 text-xs text-slate-400 sm:flex-row sm:px-8 lg:px-0">
          <div className="flex items-center gap-3"><BrandMark /><span>© 2026 BitNova. All rights reserved.</span></div>
          <div className="flex flex-wrap justify-center gap-5"><Link href="/terms" className="transition hover:text-white">Terms</Link><span>|</span><Link href="/privacy" className="transition hover:text-white">Privacy</Link><span>|</span><Link href="/risk-disclosure" className="transition hover:text-white">Risk Disclosure</Link><span>|</span><Link href="/support" className="transition hover:text-white">Support</Link></div>
        </div>
      </footer>
    </main>
  );
}
