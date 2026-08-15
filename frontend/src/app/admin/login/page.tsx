"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { adminLogin } from "@/lib/adminApi";

export default function AdminLogin() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
    <main className="flex min-h-screen items-center justify-center bg-[#070b14] px-5 text-slate-100">
      <div className="grid w-full max-w-5xl overflow-hidden rounded-3xl border border-slate-800 bg-[#0b111e] shadow-2xl shadow-black/30 lg:grid-cols-2">
        <div className="hidden bg-gradient-to-br from-cyan-500/15 via-transparent to-blue-500/10 p-10 lg:block"><div className="text-lg font-bold">BitNova</div><div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-cyan-400">Admin Console</div><div className="mt-24 max-w-sm"><div className="mb-4 inline-flex rounded-full border border-cyan-500/20 bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-300">Secure operations</div><h1 className="text-4xl font-bold leading-tight">Control the exchange with confidence.</h1><p className="mt-5 text-sm leading-6 text-slate-400">Manage users, KYC, deposits, withdrawals, orders and audit activity with role-based access control.</p></div></div>
        <div className="p-7 sm:p-10"><div className="lg:hidden"><div className="text-lg font-bold">BitNova</div><div className="text-[10px] font-semibold uppercase tracking-[0.22em] text-cyan-400">Admin Console</div></div><div className="mt-10 lg:mt-16"><h2 className="text-2xl font-bold">Admin sign in</h2><p className="mt-2 text-sm text-slate-500">Use your administrator credentials to continue.</p></div>
          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <label className="block"><span className="text-sm font-medium text-slate-300">Email</span><input value={email} onChange={(e) => setEmail(e.target.value)} name="email" type="email" required autoComplete="username" placeholder="admin@bitnova.in" className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950/60 px-4 py-3 text-sm outline-none placeholder:text-slate-600 focus:border-cyan-500" /></label>
            <label className="block"><div className="flex justify-between"><span className="text-sm font-medium text-slate-300">Password</span><span className="text-xs text-slate-600">Protected</span></div><input value={password} onChange={(e) => setPassword(e.target.value)} name="password" type="password" required autoComplete="current-password" placeholder="••••••••••••" className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950/60 px-4 py-3 text-sm outline-none placeholder:text-slate-600 focus:border-cyan-500" /></label>
            {error && <div role="alert" className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</div>}
            <button disabled={loading} type="submit" className="w-full rounded-xl bg-cyan-500 px-4 py-3 text-sm font-bold text-slate-950 hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60">{loading ? "Signing in…" : "Sign in"}</button>
          </form>
          <div className="mt-8 flex items-center justify-between border-t border-slate-800 pt-5 text-xs text-slate-600"><span>RBAC protected</span><Link href="/" className="hover:text-slate-400">Back to exchange</Link></div>
        </div>
      </div>
    </main>
  );
}
