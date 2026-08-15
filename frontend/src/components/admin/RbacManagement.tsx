"use client";

import { useCallback, useEffect, useState } from "react";
import { adminFetch } from "@/lib/adminApi";

type Permission = { id: string; name: string; description: string | null };
type Role = { id: string; name: string; description: string | null; is_active: boolean; permissions: Permission[]; user_count: number };
type Admin = { id: string; email: string; full_name: string; is_active: boolean; is_locked: boolean; roles: string[]; last_login_at: string | null };

export default function RbacManagement() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [admins, setAdmins] = useState<Admin[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [selected, setSelected] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [rolesRes, adminsRes, permissionsRes] = await Promise.all([
        adminFetch("/api/v1/admin/rbac/roles"),
        adminFetch("/api/v1/admin/rbac/admins"),
        adminFetch("/api/v1/admin/rbac/permissions"),
      ]);
      const roleData = (await rolesRes.json()) as Role[] & { detail?: string };
      const adminData = (await adminsRes.json()) as { items: Admin[]; total: number } & { detail?: string };
      const permissionData = (await permissionsRes.json()) as Permission[] & { detail?: string };
      if (!rolesRes.ok) throw new Error(roleData.detail || "Unable to load roles");
      if (!adminsRes.ok) throw new Error(adminData.detail || "Unable to load admin users");
      if (!permissionsRes.ok) throw new Error(permissionData.detail || "Unable to load permissions");
      setRoles(roleData); setAdmins(adminData.items); setPermissions(permissionData);
      const defaults: Record<string, string> = {};
      adminData.items.forEach((admin) => { if (admin.roles[0]) defaults[admin.id] = admin.roles[0]; });
      setSelected(defaults);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to load RBAC data"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { void load(); }, [load]);

  async function saveRole(admin: Admin) {
    const roleName = selected[admin.id];
    const role = roles.find((item) => item.name === roleName);
    if (!role) return;
    const reason = window.prompt(`Reason for assigning ${role.name}:`);
    if (!reason || reason.trim().length < 3) return;
    setSaving(admin.id); setError(""); setNotice("");
    try {
      const response = await adminFetch(`/api/v1/admin/rbac/admins/${admin.id}/roles`, {
        method: "PATCH", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role_ids: [role.id], reason: reason.trim() }),
      });
      const data = (await response.json()) as { roles: string[]; detail?: string };
      if (!response.ok) throw new Error(data.detail || "Unable to update role");
      setAdmins((items) => items.map((item) => item.id === admin.id ? { ...item, roles: data.roles } : item));
      setNotice(`Role updated for ${admin.email}.`);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to update role"); }
    finally { setSaving(null); }
  }

  return <div className="mx-auto max-w-7xl space-y-6">
    <div><h2 className="text-2xl font-bold tracking-tight">Admin RBAC</h2><p className="mt-2 text-sm text-slate-500">Manage administrator roles and review the permissions granted by each role.</p></div>
    {error && <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-3 text-sm text-red-300">{error}</div>}
    {notice && <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3 text-sm text-emerald-300">{notice}</div>}
    <div className="grid gap-6 xl:grid-cols-[1.25fr_1fr]">
      <section className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5">
        <div className="flex items-center justify-between"><div><h3 className="font-semibold">Administrator accounts</h3><p className="mt-1 text-xs text-slate-500">Role changes are audited and require ADMIN_MANAGE.</p></div><button onClick={() => void load()} className="rounded-lg border border-slate-700 px-3 py-2 text-xs font-semibold text-slate-300">Refresh</button></div>
        <div className="mt-5 overflow-x-auto"><table className="w-full min-w-[700px] text-left text-sm"><thead className="border-b border-slate-800 text-xs uppercase tracking-wider text-slate-500"><tr><th className="pb-3">Administrator</th><th className="pb-3">Status</th><th className="pb-3">Role</th><th className="pb-3 text-right">Action</th></tr></thead><tbody>{loading ? <tr><td colSpan={4} className="py-12 text-center text-slate-500">Loading RBAC...</td></tr> : admins.map((admin) => <tr key={admin.id} className="border-b border-slate-800/70 last:border-0"><td className="py-4"><div className="font-semibold text-slate-200">{admin.full_name}</div><div className="mt-1 text-xs text-slate-500">{admin.email}</div></td><td className="py-4"><span className={admin.is_active && !admin.is_locked ? "rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs text-emerald-300" : "rounded-full bg-red-500/10 px-2.5 py-1 text-xs text-red-300"}>{admin.is_locked ? "Locked" : admin.is_active ? "Active" : "Inactive"}</span></td><td className="py-4"><select value={selected[admin.id] || ""} onChange={(e) => setSelected((v) => ({ ...v, [admin.id]: e.target.value }))} className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-300"><option value="">Select role</option>{roles.filter((r) => r.is_active).map((role) => <option key={role.id} value={role.name}>{role.name}</option>)}</select></td><td className="py-4 text-right"><button disabled={!selected[admin.id] || saving === admin.id} onClick={() => void saveRole(admin)} className="rounded-lg bg-cyan-500 px-3 py-2 text-xs font-bold text-slate-950 disabled:opacity-40">{saving === admin.id ? "Saving..." : "Save"}</button></td></tr>)}</tbody></table></div>
      </section>
      <section className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5"><h3 className="font-semibold">Role matrix</h3><p className="mt-1 text-xs text-slate-500">{permissions.length} permissions across {roles.length} seeded roles.</p><div className="mt-5 space-y-3">{roles.map((role) => <details key={role.id} className="rounded-xl border border-slate-800 bg-slate-900/40 p-4"><summary className="cursor-pointer list-none"><div className="flex items-center justify-between"><span className="font-medium text-slate-200">{role.name}</span><span className="text-xs text-slate-500">{role.user_count} users · {role.permissions.length} permissions</span></div><div className="mt-1 text-xs text-slate-500">{role.description}</div></summary><div className="mt-4 flex flex-wrap gap-2">{role.permissions.map((permission) => <span key={permission.id} title={permission.description || ""} className="rounded-full border border-slate-700 bg-slate-950 px-2.5 py-1 text-[11px] text-slate-400">{permission.name}</span>)}</div></details>)}</div></section>
    </div>
  </div>;
}
