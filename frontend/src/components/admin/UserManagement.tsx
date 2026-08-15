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

type UserResponse = { items: User[]; page: number; page_size: number; total: number };

function formatDate(value: string | null) {
  if (!value) return "Never";
  return new Date(value).toLocaleString();
}

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState("all");
  const [verifiedFilter, setVerifiedFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ page: String(page), page_size: "25" });
      if (search.trim()) params.set("search", search.trim());
      if (activeFilter !== "all") params.set("is_active", activeFilter);
      if (verifiedFilter !== "all") params.set("is_verified", verifiedFilter);
      const response = await adminFetch(`/api/v1/admin/users?${params}`);
      const data = (await response.json()) as UserResponse & { detail?: string };
      if (!response.ok) throw new Error(data.detail || "Unable to load users");
      setUsers(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load users");
    } finally {
      setLoading(false);
    }
  }, [page, search, activeFilter, verifiedFilter]);

  useEffect(() => { void loadUsers(); }, [loadUsers]);

  async function toggleUser(user: User) {
    const reason = window.prompt(user.is_active ? "Reason for suspension:" : "Reason for activation:");
    if (!reason || reason.trim().length < 3) return;
    setActionId(user.id);
    setError("");
    setNotice("");
    try {
      const endpoint = user.is_active ? "suspend" : "activate";
      const response = await adminFetch(`/api/v1/admin/users/${user.id}/${endpoint}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: reason.trim() }),
      });
      const data = (await response.json()) as User & { detail?: string };
      if (!response.ok) throw new Error(data.detail || "User action failed");
      setUsers((current) => current.map((item) => item.id === user.id ? data : item));
      setNotice(user.is_active ? "User suspended successfully." : "User activated successfully.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "User action failed");
    } finally {
      setActionId(null);
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / 25));

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div>
        <div className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-400">Operations</div>
        <h2 className="mt-2 text-2xl font-bold tracking-tight text-white">User management</h2>
        <p className="mt-2 text-sm text-slate-500">Search, review and control customer accounts.</p>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5 shadow-xl shadow-black/10">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
          <input value={search} onChange={(e) => { setPage(1); setSearch(e.target.value); }} placeholder="Search by email..." className="w-full rounded-xl border border-slate-700 bg-slate-950/50 px-4 py-2.5 text-sm text-slate-200 outline-none placeholder:text-slate-600 focus:border-cyan-500 lg:max-w-md" />
          <select value={activeFilter} onChange={(e) => { setPage(1); setActiveFilter(e.target.value); }} className="rounded-xl border border-slate-700 bg-slate-950/50 px-3 py-2.5 text-sm text-slate-300 outline-none"><option value="all">All account status</option><option value="true">Active</option><option value="false">Suspended</option></select>
          <select value={verifiedFilter} onChange={(e) => { setPage(1); setVerifiedFilter(e.target.value); }} className="rounded-xl border border-slate-700 bg-slate-950/50 px-3 py-2.5 text-sm text-slate-300 outline-none"><option value="all">All KYC status</option><option value="true">Verified</option><option value="false">Unverified</option></select>
          <button onClick={() => void loadUsers()} className="rounded-xl border border-slate-700 px-4 py-2.5 text-sm font-semibold text-slate-300 hover:border-slate-500">Refresh</button>
        </div>

        {error && <div className="mt-4 rounded-xl border border-red-500/20 bg-red-500/5 p-3 text-sm text-red-300">{error}</div>}
        {notice && <div className="mt-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3 text-sm text-emerald-300">{notice}</div>}

        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="border-b border-slate-800 text-xs uppercase tracking-wider text-slate-500"><tr><th className="pb-3 pr-4">User</th><th className="pb-3 pr-4">Account</th><th className="pb-3 pr-4">KYC</th><th className="pb-3 pr-4">2FA</th><th className="pb-3 pr-4">Last login</th><th className="pb-3 text-right">Action</th></tr></thead>
            <tbody>
              {loading ? <tr><td colSpan={6} className="py-12 text-center text-slate-500">Loading users...</td></tr> : users.length === 0 ? <tr><td colSpan={6} className="py-12 text-center text-slate-500">No users found.</td></tr> : users.map((user) => (
                <tr key={user.id} className="border-b border-slate-800/70 last:border-0 hover:bg-slate-950/30">
                  <td className="py-4 pr-4"><Link href={`/admin/users/${user.id}`} className="block group"><div className="font-semibold text-slate-200 group-hover:text-cyan-300">{user.email}</div><div className="mt-1 text-xs text-slate-600">{user.id}</div></Link></td>
                  <td className="py-4 pr-4"><span className={user.is_active ? "rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs text-emerald-300" : "rounded-full bg-red-500/10 px-2.5 py-1 text-xs text-red-300"}>{user.is_active ? "Active" : "Suspended"}</span></td>
                  <td className="py-4 pr-4 text-slate-400">{user.is_verified ? "Verified" : "Unverified"}</td>
                  <td className="py-4 pr-4 text-slate-400">{user.two_factor_enabled ? "Enabled" : "Disabled"}</td>
                  <td className="py-4 pr-4 text-slate-500">{formatDate(user.last_login_at)}</td>
                  <td className="py-4 text-right"><div className="flex justify-end gap-2"><Link href={`/admin/users/${user.id}`} className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:border-cyan-500 hover:text-cyan-300">View</Link><button disabled={actionId === user.id} onClick={() => void toggleUser(user)} className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:border-slate-500 disabled:opacity-50">{actionId === user.id ? "Saving..." : user.is_active ? "Suspend" : "Activate"}</button></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-5 flex items-center justify-between text-xs text-slate-500"><span>{total} total users · Page {page} of {totalPages}</span><div className="flex gap-2"><button disabled={page <= 1 || loading} onClick={() => setPage((p) => p - 1)} className="rounded-lg border border-slate-700 px-3 py-2 disabled:opacity-40">Previous</button><button disabled={page >= totalPages || loading} onClick={() => setPage((p) => p + 1)} className="rounded-lg border border-slate-700 px-3 py-2 disabled:opacity-40">Next</button></div></div>
      </div>
    </div>
  );
}
