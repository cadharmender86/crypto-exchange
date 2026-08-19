"use client";

import { FormEvent, useState } from "react";
import DashboardHeader from "@/components/dashboard/DashboardHeader";
import MobileBottomNav from "@/components/layout/MobileBottomNav";
import Sidebar from "@/components/layout/Sidebar";
import { ApiError, changePassword, getAccessToken } from "@/lib/api";

const fields = [
  { label: "Full name", value: "Dharmender Kumar" },
  { label: "Email address", value: "dharmender@example.com" },
  { label: "Mobile number", value: "+91 98765 43210" },
  { label: "Country / Region", value: "India" },
];

function CheckIcon() {
  return <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/15 text-xs font-bold text-emerald-400">✓</span>;
}

export default function ProfilePage() {
  const [editing, setEditing] = useState(false);
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");
  const [passwordLoading, setPasswordLoading] = useState(false);

  function closePasswordDialog() {
    setPasswordDialogOpen(false);
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setPasswordError("");
  }

  async function handlePasswordChange(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPasswordError("");
    setPasswordSuccess("");

    if (newPassword !== confirmPassword) {
      setPasswordError("New password and confirmation do not match.");
      return;
    }

    const token = getAccessToken();
    if (!token) {
      setPasswordError("Please sign in again before changing your password.");
      return;
    }

    setPasswordLoading(true);
    try {
      const result = await changePassword(token, currentPassword, newPassword);
      setPasswordSuccess(result.message);
      closePasswordDialog();
    } catch (error) {
      setPasswordError(error instanceof ApiError ? error.message : "Unable to change your password. Please try again.");
    } finally {
      setPasswordLoading(false);
    }
  }

  return (
    <main className="min-h-screen w-full overflow-x-hidden bg-[#080d12] pb-16 text-white lg:pb-0">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-[240px] lg:block">
        <Sidebar />
      </aside>

      <section className="min-w-0 lg:ml-[240px]">
        <DashboardHeader />

        <div className="mx-auto w-full max-w-[1162px] px-4 py-6 md:px-5 lg:px-[18px]">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-medium text-blue-400">Account settings</p>
              <h1 className="mt-1 text-3xl font-bold tracking-tight">My Profile</h1>
              <p className="mt-2 text-sm text-slate-400">Manage your personal information and account security.</p>
            </div>
            <button
              onClick={() => setEditing((value) => !value)}
              className="rounded-lg border border-blue-500/35 bg-blue-500/10 px-5 py-2.5 text-sm font-semibold text-blue-300 hover:bg-blue-500/20"
            >
              {editing ? "Save changes" : "Edit profile"}
            </button>
          </div>

          <section className="mt-6 overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0d141c] shadow-[0_18px_55px_rgba(0,0,0,.18)]">
            <div className="relative overflow-hidden px-5 py-6 sm:px-7">
              <div className="absolute -right-16 -top-20 h-52 w-52 rounded-full bg-blue-600/15 blur-3xl" />
              <div className="relative flex flex-col gap-5 sm:flex-row sm:items-center">
                <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 text-2xl font-black shadow-lg shadow-blue-600/20">DK</div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="text-xl font-bold">Dharmender Kumar</h2>
                    <span className="rounded-full border border-emerald-400/25 bg-emerald-400/10 px-2.5 py-1 text-xs font-semibold text-emerald-300">Verified</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-400">Member since January 2025</p>
                  <div className="mt-4 h-2 max-w-md overflow-hidden rounded-full bg-white/[0.08]"><div className="h-full w-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400" /></div>
                  <p className="mt-2 text-xs text-slate-400">Your profile is 100% complete.</p>
                </div>
              </div>
            </div>
          </section>

          <div className="mt-5 grid gap-5 xl:grid-cols-[1.55fr_1fr]">
            <section className="rounded-2xl border border-white/[0.08] bg-[#0d141c] p-5 sm:p-6">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h2 className="text-lg font-bold">Personal information</h2>
                  <p className="mt-1 text-sm text-slate-400">Keep your details accurate and up to date.</p>
                </div>
                {editing && <span className="rounded-full bg-amber-400/10 px-3 py-1 text-xs font-semibold text-amber-300">Editing</span>}
              </div>

              <dl className="mt-5 divide-y divide-white/[0.07] rounded-xl border border-white/[0.07] bg-[#080d12]/60 px-4">
                {fields.map((field) => (
                  <div key={field.label} className="flex flex-col gap-1 py-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
                    <dt className="text-sm text-slate-400">{field.label}</dt>
                    <dd className="text-sm font-medium text-slate-100">
                      {editing && (field.label === "Email address" || field.label === "Mobile number") ? (
                        <input aria-label={field.label} defaultValue={field.value} className="w-full rounded-md border border-blue-500/35 bg-[#111c28] px-3 py-1.5 text-right text-sm text-white outline-none focus:border-blue-400 sm:w-64" />
                      ) : field.value}
                    </dd>
                  </div>
                ))}
              </dl>
            </section>

            <div className="space-y-5">
              <section className="rounded-2xl border border-white/[0.08] bg-[#0d141c] p-5 sm:p-6">
                <h2 className="text-lg font-bold">Verification</h2>
                <p className="mt-1 text-sm text-slate-400">Your limits and access are ready.</p>
                <div className="mt-5 space-y-4">
                  <div className="flex items-start gap-3"><CheckIcon /><div><p className="text-sm font-semibold">Identity verified</p><p className="mt-0.5 text-xs text-slate-400">KYC Level 2 completed</p></div></div>
                  <div className="flex items-start gap-3"><CheckIcon /><div><p className="text-sm font-semibold">Email verified</p><p className="mt-0.5 text-xs text-slate-400">dharmender@example.com</p></div></div>
                  <div className="flex items-start gap-3"><CheckIcon /><div><p className="text-sm font-semibold">Phone verified</p><p className="mt-0.5 text-xs text-slate-400">+91 98765 43210</p></div></div>
                </div>
              </section>

              <section className="rounded-2xl border border-white/[0.08] bg-[#0d141c] p-5 sm:p-6">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-bold">Security</h2>
                    <p className="mt-1 text-sm text-slate-400">Protect your account and assets.</p>
                  </div>
                  <span className="text-2xl">🔒</span>
                </div>
                <div className="mt-5 rounded-xl border border-white/[0.07] bg-[#080d12]/60 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div><p className="text-sm font-semibold">Two-factor authentication</p><p className="mt-1 text-xs text-slate-400">Add another layer of security.</p></div>
                    <button onClick={() => setTwoFactorEnabled((value) => !value)} className={`relative h-6 w-11 rounded-full transition ${twoFactorEnabled ? "bg-blue-600" : "bg-slate-600"}`} aria-label="Toggle two-factor authentication" aria-pressed={twoFactorEnabled}>
                      <span className={`absolute top-1 h-4 w-4 rounded-full bg-white transition ${twoFactorEnabled ? "left-6" : "left-1"}`} />
                    </button>
                  </div>
                </div>
                <button onClick={() => { setPasswordSuccess(""); setPasswordDialogOpen(true); }} className="mt-4 text-sm font-semibold text-blue-400 hover:text-blue-300">Change password →</button>
                {passwordSuccess && <p className="mt-3 text-xs font-medium text-emerald-400">{passwordSuccess}</p>}
              </section>
            </div>
          </div>

          <section className="mt-5 rounded-2xl border border-white/[0.08] bg-[#0d141c] p-5 sm:p-6">
            <h2 className="text-lg font-bold">Recent account activity</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {["Successful sign-in · New Delhi, IN", "Password changed · Jan 18, 2025", "KYC verification completed · Jan 12, 2025"].map((activity) => (
                <div key={activity} className="rounded-xl border border-white/[0.07] bg-[#080d12]/60 p-4 text-sm text-slate-300">{activity}</div>
              ))}
            </div>
          </section>
        </div>
      </section>

      {passwordDialogOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="change-password-title">
          <form onSubmit={handlePasswordChange} className="w-full max-w-md rounded-2xl border border-white/10 bg-[#111923] p-6 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <div><h2 id="change-password-title" className="text-xl font-bold">Change password</h2><p className="mt-1 text-sm text-slate-400">Use at least 8 characters and choose a password you do not use elsewhere.</p></div>
              <button type="button" onClick={closePasswordDialog} className="rounded-md px-2 py-1 text-lg text-slate-400 hover:bg-white/10 hover:text-white" aria-label="Close dialog">×</button>
            </div>
            <div className="mt-6 space-y-4">
              <label className="block text-sm font-medium text-slate-200">Current password<input type="password" required minLength={8} maxLength={128} value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} className="mt-1.5 w-full rounded-lg border border-white/10 bg-[#080d12] px-3 py-2.5 text-white outline-none focus:border-blue-500" /></label>
              <label className="block text-sm font-medium text-slate-200">New password<input type="password" required minLength={8} maxLength={128} value={newPassword} onChange={(event) => setNewPassword(event.target.value)} className="mt-1.5 w-full rounded-lg border border-white/10 bg-[#080d12] px-3 py-2.5 text-white outline-none focus:border-blue-500" /></label>
              <label className="block text-sm font-medium text-slate-200">Confirm new password<input type="password" required minLength={8} maxLength={128} value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} className="mt-1.5 w-full rounded-lg border border-white/10 bg-[#080d12] px-3 py-2.5 text-white outline-none focus:border-blue-500" /></label>
            </div>
            {passwordError && <p className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2.5 text-sm text-red-300">{passwordError}</p>}
            <div className="mt-6 flex justify-end gap-3"><button type="button" onClick={closePasswordDialog} className="rounded-lg px-4 py-2.5 text-sm font-semibold text-slate-300 hover:bg-white/5">Cancel</button><button type="submit" disabled={passwordLoading} className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60">{passwordLoading ? "Updating..." : "Update password"}</button></div>
          </form>
        </div>
      )}

      <MobileBottomNav />
    </main>
  );
}
