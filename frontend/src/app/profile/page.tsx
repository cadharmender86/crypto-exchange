"use client";

import Link from "next/link";
import Sidebar from "../../components/layout/Sidebar";
import DashboardHeader from "../../components/dashboard/DashboardHeader";

const InfoRow = ({ label, value, action }: { label: string; value: string; action?: string }) => (
  <div className="flex items-center justify-between gap-4 border-b border-white/[0.06] py-4 last:border-b-0">
    <div>
      <p className="text-[11px] text-slate-500">{label}</p>
      <p className="mt-1 text-sm font-medium text-slate-100">{value}</p>
    </div>
    {action && <button className="text-xs font-semibold text-cyan-400 hover:text-cyan-300">{action}</button>}
  </div>
);

const SecurityRow = ({ icon, title, description, status, action }: { icon: string; title: string; description: string; status: string; action: string }) => (
  <div className="flex items-center gap-4 border-b border-white/[0.06] py-4 last:border-b-0">
    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/[0.06] text-lg text-cyan-300">{icon}</div>
    <div className="min-w-0 flex-1">
      <div className="flex items-center gap-2">
        <p className="text-sm font-semibold text-white">{title}</p>
        <span className="rounded-full bg-emerald-400/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-400">{status}</span>
      </div>
      <p className="mt-1 text-xs text-slate-500">{description}</p>
    </div>
    <button className="rounded-lg border border-white/10 px-3 py-2 text-xs font-semibold text-slate-200 hover:border-cyan-400/30 hover:text-cyan-300">{action}</button>
  </div>
);

export default function ProfilePage() {
  return (
    <main className="min-h-screen w-full overflow-x-hidden bg-[#080d12] text-white">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-[180px] lg:block [&>aside]:w-full"><Sidebar /></aside>
      <section className="min-w-0 lg:ml-[180px]">
        <DashboardHeader />
        <div className="mx-auto w-full max-w-[1162px] px-4 py-5 md:px-5 lg:px-[18px]">
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400">Account</p>
              <h1 className="mt-1 text-2xl font-bold tracking-tight md:text-[28px]">My Profile</h1>
              <p className="mt-1 text-xs text-slate-400">Manage your personal information, verification and account security.</p>
            </div>
            <Link href="/dashboard" className="w-fit rounded-lg border border-white/10 px-4 py-2 text-xs font-semibold text-slate-200 hover:border-cyan-400/30 hover:text-cyan-300">← Back to Dashboard</Link>
          </div>

          <section className="mb-4 rounded-2xl border border-white/[0.07] bg-[#0d141b] p-5 shadow-[0_12px_40px_rgba(0,0,0,.18)] md:p-6">
            <div className="flex flex-col gap-5 md:flex-row md:items-center">
              <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-400 text-2xl font-bold text-white shadow-lg shadow-blue-600/20">DK</div>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="text-xl font-bold">Dharmender Kumar</h2>
                  <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2.5 py-1 text-[10px] font-semibold text-emerald-400">Active</span>
                </div>
                <p className="mt-1 text-sm text-slate-400">customer@example.com</p>
                <p className="mt-2 text-xs text-slate-500">Member since 2026 · Customer ID: BN-••••••</p>
              </div>
              <div className="rounded-xl border border-emerald-400/10 bg-emerald-400/[0.04] px-4 py-3 text-center">
                <p className="text-[10px] uppercase tracking-wider text-slate-500">Account status</p>
                <p className="mt-1 text-sm font-bold text-emerald-400">Verified</p>
              </div>
            </div>
          </section>

          <div className="grid gap-4 xl:grid-cols-[1.15fr_.85fr]">
            <section className="rounded-2xl border border-white/[0.07] bg-[#0d141b] px-5 md:px-6">
              <div className="border-b border-white/[0.06] py-5">
                <h2 className="text-base font-bold">Personal Information</h2>
                <p className="mt-1 text-xs text-slate-500">Your registered account details.</p>
              </div>
              <InfoRow label="Full Name" value="Dharmender Kumar" action="Edit" />
              <InfoRow label="Email Address" value="customer@example.com" action="Change" />
              <InfoRow label="Mobile Number" value="+91 ••••• •••••" action="Change" />
              <InfoRow label="Date of Birth" value="•• / •• / ••••" />
              <InfoRow label="Country / Region" value="India" />
            </section>

            <section className="rounded-2xl border border-white/[0.07] bg-[#0d141b] px-5 md:px-6">
              <div className="border-b border-white/[0.06] py-5">
                <h2 className="text-base font-bold">Verification</h2>
                <p className="mt-1 text-xs text-slate-500">Complete verification to unlock account limits.</p>
              </div>
              <div className="flex items-center justify-between gap-4 border-b border-white/[0.06] py-5">
                <div><p className="text-sm font-semibold">Identity Verification</p><p className="mt-1 text-xs text-slate-500">KYC verification status</p></div>
                <span className="rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-400">Verified</span>
              </div>
              <div className="flex items-center justify-between gap-4 border-b border-white/[0.06] py-5">
                <div><p className="text-sm font-semibold">Bank Account</p><p className="mt-1 text-xs text-slate-500">INR withdrawals and deposits</p></div>
                <span className="rounded-full bg-amber-400/10 px-3 py-1 text-xs font-semibold text-amber-400">Pending</span>
              </div>
              <Link href="/kyc" className="my-5 inline-flex rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 px-4 py-2.5 text-xs font-bold text-white shadow-lg shadow-blue-600/20">Manage Verification →</Link>
            </section>
          </div>

          <section className="mt-4 rounded-2xl border border-white/[0.07] bg-[#0d141b] px-5 md:px-6">
            <div className="border-b border-white/[0.06] py-5">
              <h2 className="text-base font-bold">Security</h2>
              <p className="mt-1 text-xs text-slate-500">Protect your BitNova account and transactions.</p>
            </div>
            <SecurityRow icon="🔐" title="Password" description="Last changed recently" status="Protected" action="Change" />
            <SecurityRow icon="✓" title="Two-Factor Authentication" description="Add an extra layer of protection to your account" status="Recommended" action="Enable" />
            <SecurityRow icon="◉" title="Login Activity" description="Review recent sessions and devices" status="Monitored" action="View" />
          </section>

          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <section className="rounded-2xl border border-white/[0.07] bg-[#0d141b] p-5 md:p-6">
              <h2 className="text-base font-bold">Preferences</h2>
              <div className="mt-4 flex items-center justify-between"><div><p className="text-sm font-semibold">Email Notifications</p><p className="text-xs text-slate-500">Security and transaction alerts</p></div><span className="rounded-full bg-blue-500/15 px-3 py-1 text-xs font-semibold text-blue-300">On</span></div>
              <div className="mt-4 flex items-center justify-between"><div><p className="text-sm font-semibold">Default Currency</p><p className="text-xs text-slate-500">Prices displayed in dashboard</p></div><span className="text-sm font-semibold">INR</span></div>
            </section>
            <section className="rounded-2xl border border-red-500/10 bg-[#0d141b] p-5 md:p-6">
              <h2 className="text-base font-bold">Account Actions</h2>
              <p className="mt-2 text-xs leading-5 text-slate-500">For your security, withdrawals should be completed before closing an account.</p>
              <button className="mt-4 rounded-lg border border-red-400/20 px-4 py-2.5 text-xs font-semibold text-red-400 hover:bg-red-400/5">Request Account Closure</button>
            </section>
          </div>

          <p className="mt-6 text-center text-[11px] text-slate-600">BitNova never asks for your password, OTP or private keys.</p>
        </div>
      </section>
    </main>
  );
}
