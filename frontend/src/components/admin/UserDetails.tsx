"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { adminFetch } from "@/lib/adminApi";

type User = {
  id: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  two_factor_enabled: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
};

type AuditLog = {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  result: string;
  reason: string | null;
  created_at: string;
};

function formatDate(value: string | null) {
  if (!value) return "Never";
  return new Date(value).toLocaleString();
}

function Status({ active, children }: { active: boolean; children: React.ReactNode }) {
  return <span className={active ? "rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-300" : "rounded-full bg-red-500/10 px-2.5 py-1 text-xs font-medium text-red-300"}>{children}</span>;
}

export default function UserDetails({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await adminFetch(`/api/v1/admin/users/${userId}`);
      const data = (await response.json()) as User & { detail?: string };
      if (!response.ok) throw new Error(data.detail || "Unable to load user");
      setUser(data);

      try {
        const auditResponse = await adminFetch(`/api/v1/admin/audit-logs?limit=100`);
        if (auditResponse.ok) {
          const auditData = (await auditResponse.json()) as AuditLog[];
          setLogs(auditData.filter((log) => log.resource_type === "USER" && log.resource_id === userId).slice(0, 10));
        }
      } catch {
        // Audit history is optional for admins without AUDIT_READ permission.
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load user");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => { void load(); }, [load]);

  async function changeStatus() {
    if (!user) return;
    const nextAction = user.is_active ? "suspend" : "activate";
    const reason = window.prompt(user.is_active ? "Reason for suspension:" : "Reason for activation:");
    if (!reason || reason.trim().length < 3) return;

    setActionLoading(true);
    setError("");
    setNotice("");
    try {
      const response = await adminFetch(`/api/v1/admin/users/${user.id}/${nextAction}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: reason.trim() }),
      });
      const data = (await response.json()) as User & { detail?: string };
      if (!response.ok) throw new Error(data.detail || "User action failed");
      setUser(data);
      setNotice(user.is_active ? "User suspended successfully." : "User activated successfully.");
      void load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "User action failed");
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) return <div className="mx-auto max-w-7xl rounded-2xl border border-slate-800 bg-[#0d1422] p-10 text-center text-sm text-slate-500">Loading user...</div>;
  if (!user) return <div className="mx-auto max-w-7xl space-y-4"><Link href="/admin/users" className="text-sm text-cyan-400 hover:text-cyan-300">← Back to users</Link><div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-5 text-sm text-red-300">{error || "User not found."}</div></div>;

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <Link href="/admin/users" className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400 hover:text-cyan-300">← User management</Link>
          <h2 className="mt-3 text-2xl font-bold tracking-tight text-white">User details</h2>
          <p className="mt-2 text-sm text-slate-500">Review the customer account and perform authorized account controls.</p>
        </div>
        <div className="flex items-center gap-3">
          <Status active={user.is_active}>{user.is_active ? "Active" : "Suspended"}</Status>
          <button disabled={actionLoading} onClick={() => void changeStatus()} className={user.is_active ? "rounded-xl border border-red-500/30 bg-red-500/5 px-4 py-2.5 text-sm font-semibold text-red-300 hover:bg-red-500/10 disabled:opacity-50" : "rounded-xl border border-emerald-500/30 bg-emerald-500/5 px-4 py-2.5 text-sm font-semibold text-emerald-300 hover:bg-emerald-500/10 disabled:opacity-50"}>{actionLoading ? "Saving..." : user.is_active ? "Suspend account" : "Activate account"}</button>
        </div>
      </div>

      {error && <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-3 text-sm text-red-300">{error}</div>}
      {notice && <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3 text-sm text-emerald-300">{notice}</div>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5"><div className="text-xs uppercase tracking-wider text-slate-500">Account status</div><div className="mt-3"><Status active={user.is_active}>{user.is_active ? "Active" : "Suspended"}</Status></div></div>
        <div className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5"><div className="text-xs uppercase tracking-wider text-slate-500">KYC status</div><div className={user.is_verified ? "mt-3 text-emerald-300" : "mt-3 text-amber-300"}>{user.is_verified ? "Verified" : "Unverified"}</div></div>
        <div className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5"><div className="text-xs uppercase tracking-wider text-slate-500">2FA</div><div className="mt-3 text-slate-200">{user.two_factor_enabled ? "Enabled" : "Disabled"}</div></div>
        <div className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5"><div className="text-xs uppercase tracking-wider text-slate-500">Last login</div><div className="mt-3 text-sm text-slate-200">{formatDate(user.last_login_at)}</div></div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
        <div className="rounded-2xl border border-slate-800 bg-[#0d1422] p-6">
          <h3 className="text-base font-semibold text-white">Account information</h3>
          <div className="mt-5 grid gap-5 sm:grid-cols-2">
            <div><div className="text-xs uppercase tracking-wider text-slate-500">Email</div><div className="mt-2 break-all text-sm text-slate-200">{user.email}</div></div>
            <div><div className="text-xs uppercase tracking-wider text-slate-500">User ID</div><div className="mt-2 break-all font-mono text-xs text-slate-400">{user.id}</div></div>
            <div><div className="text-xs uppercase tracking-wider text-slate-500">Created</div><div className="mt-2 text-sm text-slate-300">{formatDate(user.created_at)}</div></div>
            <div><div className="text-xs uppercase tracking-wider text-slate-500">Last updated</div><div className="mt-2 text-sm text-slate-300">{formatDate(user.updated_at)}</div></div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-[#0d1422] p-6">
          <h3 className="text-base font-semibold text-white">Operational modules</h3>
          <p className="mt-2 text-xs leading-5 text-slate-500">These areas will be populated as their admin APIs are connected.</p>
          <div className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-1">
            {['Wallets', 'Deposits', 'Withdrawals', 'Orders', 'Ledger'].map((item) => <div key={item} className="rounded-xl border border-slate-800 bg-slate-950/30 px-4 py-3 text-sm text-slate-400"><span className="mr-2 text-slate-600">•</span>{item}</div>)}
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-[#0d1422] p-6">
        <div className="flex items-center justify-between"><div><h3 className="text-base font-semibold text-white">User audit history</h3><p className="mt-1 text-xs text-slate-500">Administrative actions associated with this account.</p></div><span className="rounded-full border border-slate-700 px-2.5 py-1 text-xs text-slate-500">Last 10</span></div>
        <div className="mt-5 overflow-x-auto">
          {logs.length === 0 ? <div className="rounded-xl border border-dashed border-slate-800 p-8 text-center text-sm text-slate-600">No user-specific audit events available.</div> : <table className="w-full min-w-[650px] text-left text-sm"><thead className="border-b border-slate-800 text-xs uppercase tracking-wider text-slate-500"><tr><th className="pb-3 pr-4">Action</th><th className="pb-3 pr-4">Result</th><th className="pb-3 pr-4">Reason</th><th className="pb-3">Time</th></tr></thead><tbody>{logs.map((log) => <tr key={log.id} className="border-b border-slate-800/70 last:border-0"><td className="py-3 pr-4 font-medium text-slate-300">{log.action}</td><td className="py-3 pr-4"><span className="text-emerald-300">{log.result}</span></td><td className="max-w-md py-3 pr-4 text-slate-500">{log.reason || "—"}</td><td className="py-3 text-slate-500">{formatDate(log.created_at)}</td></tr>)}</tbody></table>}
        </div>
      </section>
    </div>
  );
}
