"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { ApiError, login, saveTokens } from "@/lib/api";

function MailIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5">
      <path d="M4 6.5h16v11H4z" fill="none" stroke="currentColor" strokeWidth="1.7" />
      <path d="m4.5 7 7.5 6 7.5-6" fill="none" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5">
      <rect x="5" y="10" width="14" height="10" rx="2" fill="none" stroke="currentColor" strokeWidth="1.7" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" strokeWidth="1.7" />
    </svg>
  );
}

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
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
    <main className="min-h-screen bg-[#070b12] text-white">
      <div className="mx-auto grid min-h-screen max-w-7xl lg:grid-cols-[1.05fr_0.95fr]">
        <section className="relative hidden overflow-hidden px-10 py-10 lg:flex lg:flex-col lg:justify-between xl:px-16">
          <div className="absolute -left-32 top-24 h-80 w-80 rounded-full bg-blue-500/10 blur-3xl" />
          <div className="absolute bottom-0 right-10 h-96 w-96 rounded-full bg-cyan-400/5 blur-3xl" />

          <Link href="/" className="relative inline-flex w-fit items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-blue-500 text-lg font-black shadow-lg shadow-blue-500/20">
              B
            </span>
            <span className="text-xl font-bold tracking-tight">BitNova</span>
          </Link>

          <div className="relative max-w-xl pb-12">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-blue-400/20 bg-blue-400/5 px-3 py-1.5 text-xs font-medium text-blue-300">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              Secure digital asset platform
            </div>
            <h1 className="text-5xl font-bold leading-[1.08] tracking-tight xl:text-6xl">
              Your crypto,
              <br />
              <span className="text-blue-400">your control.</span>
            </h1>
            <p className="mt-6 max-w-lg text-base leading-7 text-slate-400">
              Trade digital assets, manage your wallet and move between INR and crypto from one secure account.
            </p>

            <div className="mt-10 grid max-w-lg grid-cols-3 gap-3">
              {[
                ["24/7", "Market access"],
                ["INR", "Easy funding"],
                ["Secure", "Account controls"],
              ].map(([value, label]) => (
                <div key={label} className="rounded-2xl border border-white/8 bg-white/[0.025] p-4">
                  <p className="font-semibold text-white">{value}</p>
                  <p className="mt-1 text-xs text-slate-500">{label}</p>
                </div>
              ))}
            </div>
          </div>

          <p className="relative text-xs text-slate-600">© BitNova. Digital assets involve risk.</p>
        </section>

        <section className="flex min-h-screen items-center justify-center px-5 py-10 sm:px-8">
          <div className="w-full max-w-md">
            <div className="mb-8 flex items-center justify-between lg:hidden">
              <Link href="/" className="inline-flex items-center gap-2.5">
                <span className="grid h-9 w-9 place-items-center rounded-lg bg-blue-500 text-sm font-black">B</span>
                <span className="text-lg font-bold">BitNova</span>
              </Link>
              <Link href="/" className="text-sm text-slate-500 hover:text-slate-300">Back</Link>
            </div>

            <div className="rounded-3xl border border-white/10 bg-[#0d121b] p-6 shadow-2xl shadow-black/30 sm:p-8">
              <div>
                <p className="text-sm font-medium text-blue-400">Welcome back</p>
                <h2 className="mt-2 text-3xl font-bold tracking-tight">Sign in to BitNova</h2>
                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Access your portfolio, wallet and trading account.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="mt-8 space-y-5">
                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-slate-300">Email address</span>
                  <span className="flex items-center gap-3 rounded-xl border border-white/10 bg-[#080c13] px-4 transition focus-within:border-blue-500/70 focus-within:ring-4 focus-within:ring-blue-500/10">
                    <span className="text-slate-500"><MailIcon /></span>
                    <input
                      type="email"
                      required
                      autoComplete="email"
                      value={email}
                      onChange={(event) => setEmail(event.target.value)}
                      className="h-12 w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
                      placeholder="you@example.com"
                    />
                  </span>
                </label>

                <label className="block">
                  <span className="mb-2 block text-sm font-medium text-slate-300">Password</span>
                  <span className="flex items-center gap-3 rounded-xl border border-white/10 bg-[#080c13] px-4 transition focus-within:border-blue-500/70 focus-within:ring-4 focus-within:ring-blue-500/10">
                    <span className="text-slate-500"><LockIcon /></span>
                    <input
                      type={showPassword ? "text" : "password"}
                      required
                      autoComplete="current-password"
                      value={password}
                      onChange={(event) => setPassword(event.target.value)}
                      className="h-12 w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
                      placeholder="Enter your password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((value) => !value)}
                      className="shrink-0 text-xs font-medium text-slate-500 hover:text-slate-300"
                    >
                      {showPassword ? "Hide" : "Show"}
                    </button>
                  </span>
                </label>

                <div className="flex items-center justify-between gap-4">
                  <label className="flex cursor-pointer items-center gap-2 text-xs text-slate-500">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(event) => setRememberMe(event.target.checked)}
                      className="h-4 w-4 rounded border-white/20 bg-transparent accent-blue-500"
                    />
                    Remember me
                  </label>
                  <span className="text-xs text-slate-600">Password recovery coming soon</span>
                </div>

                {error && (
                  <div role="alert" className="rounded-xl border border-red-500/25 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="h-12 w-full rounded-xl bg-blue-500 font-semibold text-white shadow-lg shadow-blue-500/15 transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? "Signing in..." : "Sign in"}
                </button>
              </form>

              <div className="my-7 flex items-center gap-3 text-[11px] uppercase tracking-wider text-slate-700">
                <span className="h-px flex-1 bg-white/8" />
                <span>New to BitNova?</span>
                <span className="h-px flex-1 bg-white/8" />
              </div>

              <Link
                href="/register"
                className="flex h-11 w-full items-center justify-center rounded-xl border border-white/10 bg-white/[0.02] text-sm font-semibold text-slate-300 transition hover:border-white/20 hover:bg-white/[0.05] hover:text-white"
              >
                Create an account
              </Link>

              <p className="mt-6 text-center text-[11px] leading-5 text-slate-600">
                By continuing, you agree to BitNova&apos;s Terms of Service and Privacy Policy.
              </p>
            </div>

            <div className="mt-6 flex items-center justify-center gap-2 text-xs text-slate-600">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              Your connection is protected with secure transport
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
