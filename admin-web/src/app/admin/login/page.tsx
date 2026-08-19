"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { adminLogin } from "@/lib/adminApi";

function ShieldIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-8 w-8" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <path d="M12 3 19 6v5c0 4.8-2.9 8.4-7 10-4.1-1.6-7-5.2-7-10V6l7-3Z" />
      <path d="M9.5 12.2 11.2 14l3.6-4" />
    </svg>
  );
}

function ChartIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <path d="M4 19V5M4 19h16" />
      <path d="m7 15 3-4 3 2 5-6" />
    </svg>
  );
}

function ShieldSmallIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <path d="M12 3 19 6v5c0 4.8-2.9 8.4-7 10-4.1-1.6-7-5.2-7-10V6l7-3Z" />
    </svg>
  );
}

function UsersIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <circle cx="9" cy="8" r="3" />
      <path d="M3.5 19c.5-3.2 2.3-5 5.5-5s5 1.8 5.5 5" />
      <path d="M16 6.5a3 3 0 0 1 0 5.8M16 14c2.4.2 3.9 1.8 4.5 4" />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <rect x="5" y="10" width="14" height="10" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v2" />
    </svg>
  );
}

function MailIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="m4 7 8 6 8-6" />
    </svg>
  );
}

function EyeIcon({ hidden }: { hidden: boolean }) {
  return hidden ? (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <path d="m3 3 18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M9.9 5.2A10.8 10.8 0 0 1 12 5c5.2 0 8.7 4.5 9.7 7-.4 1.1-1.4 2.8-3.1 4.3M6.1 6.1C4.2 7.4 2.9 9.4 2.3 12c.6 2.5 4.2 7 9.7 7 1.2 0 2.3-.2 3.3-.6" />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <path d="M2.3 12C3.3 9.5 6.8 5 12 5s8.7 4.5 9.7 7c-1 2.5-4.5 7-9.7 7s-8.7-4.5-9.7-7Z" />
      <circle cx="12" cy="12" r="2.5" />
    </svg>
  );
}

export default function AdminLogin() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await adminLogin(email, password);
      router.replace("/admin");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen overflow-hidden bg-[#030712] text-slate-100">
      <div className="relative min-h-screen lg:grid lg:grid-cols-[minmax(0,1.08fr)_minmax(520px,0.92fr)]">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_25%,rgba(99,102,241,0.14),transparent_32%),radial-gradient(circle_at_75%_75%,rgba(245,158,11,0.08),transparent_28%)]" />

        <section className="relative hidden overflow-hidden border-r border-slate-800/80 lg:flex lg:flex-col lg:justify-between lg:p-12 xl:p-16">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-amber-400/30 bg-amber-400/10 text-amber-300 shadow-lg shadow-amber-500/10">
                <span className="text-2xl font-black">B</span>
              </div>
              <div>
                <div className="text-xl font-extrabold tracking-[0.08em]">BITNOVA</div>
                <div className="text-[10px] font-semibold uppercase tracking-[0.28em] text-violet-400">Admin Panel</div>
              </div>
            </div>

            <div className="mt-20 max-w-2xl xl:mt-24">
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-violet-500/20 bg-violet-500/10 px-3 py-1.5 text-xs font-semibold text-violet-300">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.8)]" />
                Secure exchange operations
              </div>
              <h1 className="text-4xl font-extrabold leading-[1.08] tracking-tight xl:text-6xl">
                Welcome to
                <br />
                BitNova <span className="text-violet-400">Admin</span>
              </h1>
              <p className="mt-6 max-w-xl text-base leading-7 text-slate-400 xl:text-lg">
                Securely manage users, monitor transactions, handle compliance and run the BitNova Exchange with confidence.
              </p>
            </div>

            <div className="mt-12 grid max-w-2xl gap-4 sm:grid-cols-3">
              {[
                { icon: <ChartIcon />, title: "Real-time Overview", text: "Users, trading volume, deposits and withdrawals." },
                { icon: <ShieldSmallIcon />, title: "Secure & Reliable", text: "Role-based access and activity monitoring." },
                { icon: <UsersIcon />, title: "Complete Control", text: "KYC, wallets, orders, ledger and RBAC." },
              ].map((item) => (
                <div key={item.title} className="rounded-2xl border border-slate-800/80 bg-slate-900/35 p-4 backdrop-blur-sm">
                  <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-violet-500/15 text-violet-300">{item.icon}</div>
                  <div className="text-sm font-semibold text-slate-200">{item.title}</div>
                  <div className="mt-2 text-xs leading-5 text-slate-500">{item.text}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative mt-12 max-w-3xl overflow-hidden rounded-3xl border border-slate-800/80 bg-slate-900/45 p-5 shadow-2xl shadow-black/30 backdrop-blur-sm xl:p-6">
            <div className="absolute -right-20 -top-20 h-48 w-48 rounded-full bg-violet-600/10 blur-3xl" />
            <div className="relative grid grid-cols-3 gap-4">
              {[
                ["Trading Volume", "₹152.36M", "+18.2%"],
                ["User Growth", "12,458", "+12.5%"],
                ["Withdrawals", "₹18.43M", "+9.8%"],
              ].map(([label, value, change]) => (
                <div key={label}>
                  <div className="text-[11px] text-slate-500">{label}</div>
                  <div className="mt-2 text-lg font-bold xl:text-xl">{value}</div>
                  <div className="mt-1 text-[11px] font-semibold text-emerald-400">↗ {change}</div>
                  <div className="mt-4 flex h-10 items-end gap-1 opacity-70">
                    {[30, 48, 34, 55, 44, 68, 52, 78, 65, 88].map((height, index) => (
                      <span key={index} className="flex-1 rounded-t bg-violet-500/50" style={{ height: `${height}%` }} />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8 flex flex-wrap gap-x-10 gap-y-4 border-t border-slate-800/70 pt-5 text-xs text-slate-500">
            <span>© 2026 BitNova Exchange</span>
            <span>Secure Admin Operations</span>
            <span>RBAC Protected</span>
          </div>
        </section>

        <section className="relative flex min-h-screen items-center justify-center p-5 sm:p-8 lg:p-12">
          <div className="w-full max-w-xl">
            <div className="mb-8 lg:hidden">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-400/10 text-xl font-black text-amber-300">B</div>
                <div>
                  <div className="font-extrabold tracking-[0.08em]">BITNOVA</div>
                  <div className="text-[10px] font-semibold uppercase tracking-[0.25em] text-violet-400">Admin Panel</div>
                </div>
              </div>
            </div>

            <div className="relative overflow-hidden rounded-[2rem] border border-slate-700/80 bg-[#0b1220]/95 p-7 shadow-[0_30px_100px_rgba(0,0,0,0.45)] backdrop-blur-xl sm:p-10">
              <div className="absolute -right-20 -top-20 h-48 w-48 rounded-full bg-violet-600/15 blur-3xl" />
              <div className="relative">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-violet-400/30 bg-violet-500/10 text-violet-300 shadow-lg shadow-violet-500/10">
                  <ShieldIcon />
                </div>
                <div className="mt-6 text-center">
                  <h2 className="text-3xl font-extrabold tracking-tight">Admin Sign In</h2>
                  <p className="mt-2 text-sm text-slate-500">Access your BitNova admin account</p>
                </div>

                <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
                  <label className="block">
                    <span className="text-sm font-medium text-slate-300">Email Address</span>
                    <div className="relative mt-2">
                      <MailIcon />
                      <input value={email} onChange={(e) => setEmail(e.target.value)} name="email" type="email" required autoComplete="username" placeholder="Enter your email" className="w-full rounded-xl border border-slate-700 bg-slate-950/60 py-3.5 pl-11 pr-4 text-sm outline-none transition placeholder:text-slate-600 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/10" />
                    </div>
                  </label>

                  <label className="block">
                    <span className="text-sm font-medium text-slate-300">Password</span>
                    <div className="relative mt-2">
                      <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500"><LockIcon /></span>
                      <input value={password} onChange={(e) => setPassword(e.target.value)} name="password" type={showPassword ? "text" : "password"} required autoComplete="current-password" placeholder="Enter your password" className="w-full rounded-xl border border-slate-700 bg-slate-950/60 py-3.5 pl-11 pr-12 text-sm outline-none transition placeholder:text-slate-600 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/10" />
                      <button type="button" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? "Hide password" : "Show password"} className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 transition hover:text-slate-200">
                        <EyeIcon hidden={showPassword} />
                      </button>
                    </div>
                  </label>

                  <div className="flex items-center justify-between gap-4 text-xs">
                    <label className="flex cursor-pointer items-center gap-2 text-slate-400">
                      <input type="checkbox" checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} className="h-4 w-4 rounded border-slate-700 bg-slate-900 accent-violet-500" />
                      Remember me
                    </label>
                    <span className="text-slate-600">Protected by RBAC</span>
                  </div>

                  {error && <div role="alert" className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</div>}

                  <button disabled={loading} type="submit" className="group flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-3.5 text-sm font-bold text-white shadow-lg shadow-violet-900/30 transition hover:from-violet-500 hover:to-indigo-500 disabled:cursor-not-allowed disabled:opacity-60">
                    {loading ? "Signing in…" : "Sign In"}
                    {!loading && <span className="text-lg transition-transform group-hover:translate-x-1">›</span>}
                  </button>
                </form>

                <div className="my-7 flex items-center gap-4 text-xs text-slate-600">
                  <span className="h-px flex-1 bg-slate-800" />
                  <span>Secure access</span>
                  <span className="h-px flex-1 bg-slate-800" />
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-950/35 px-4 py-3 text-center text-xs text-slate-500">
                  <span className="text-slate-400">Need help?</span> Contact your exchange administrator or IT support.
                </div>

                <div className="mt-6 flex items-center justify-between border-t border-slate-800 pt-5 text-xs text-slate-600">
                  <span>BitNova Admin Console</span>
                  <Link href="/" className="transition hover:text-slate-300">Back to exchange</Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
