"use client";

import { useCallback, useEffect, useState } from "react";
import { adminFetch } from "@/lib/adminApi";

type Permission = { id: string; name: string; description: string | null };
type Role = { id: string; name: string; description: string | null; is_active: boolean; permissions: Permission[]; user_count: number };
type Admin = { id: string; email: string; full_name: string; is_active: boolean; is_locked: boolean; roles: string[]; last_login_at: string | null };

type CreateForm = {
  full_name: string;
  email: string;
  password: string;
  role_id: string;
  reason: string;
};

const emptyForm: CreateForm = { full_name: "", email: "", password: "", role_id: "", reason: "" };

export default function RbacManagement() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [admins, setAdmins] = useState<Admin[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [selected, setSelected] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState<CreateForm>(emptyForm);
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

  async function createAdmin(event: React.FormEvent) {
    event.preventDefault();
    setCreating(true); setError(""); setNotice("");
    try {
      const response = await adminFetch("/api/v1/admin/rbac/admins", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = (await response.json()) as Admin & { detail?: string };
      if (!response.ok) throw new Error(data.detail || "Unable to create admin");
      setNotice(`Admin ${data.email} created successfully.`);
      setForm(emptyForm);
      setShowCreate(false);
      await load();
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to create admin"); }
    finally { setCreating(false); }
  }

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

  const assignableRoles = roles.filter((role) => role.is_active && role.name !== "SUPER_ADMIN");

  return <div className="mx-auto max-w-7xl space-y-6">
    <div className="flex items-start justify-between gap-4">
      <div><h2 className="text-2xl font-bold tracking-tight">Admin RBAC</h2><p className="mt-2 text-sm text-slate-500">Create staff administrators, assign controlled roles, and review effective permissions.</p></div>
      <button onClick={() => { setShowCreate(true); setError(""); setNotice(""); }} className="rounded-lg bg-cyan-500 px-4 py-2.5 text-sm font-bold text-slate-950">+ Create Admin</button>
    </div>

    {error && <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-3 text-sm text-red-300">{error}</div>}
    {notice && <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3 text-sm text-emerald-300">{notice}</div>}

    {showCreate && <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4">
      <form onSubmit={createAdmin} className="w-full max-w-lg rounded-2xl border border-slate-700 bg-[#0d1422] p-6 shadow-2xl">
        <div className="flex items-center justify-between"><div><h3 className="text-lg font-semibold text-slate-100">Create Staff Admin</h3><p className="mt-1 text-xs text-slate-500">Only non-Super Admin roles can be created here.</p></div><button type="button" onClick={() => setShowCreate(false)} className="text-slate-500 hover:text-slate-200">✕</button></div>
        <div className="mt-5 grid gap-4">
          <label className="text-sm text-slate-300">Full name<input required minLength={2} maxLength={255} value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} className="mt-1.5 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-200 outline-none" /></label>
          <label className="text-sm text-slate-300">Email<input required type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="mt-1.5 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-200 outline-none" /></label>
          <label className="text-sm text-slate-300">Initial password<input required type="password" minLength={12} maxLength={128} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Minimum 12 characters" className="mt-1.5 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-200 outline-none" /></label>
          <label className="text-sm text-slate-300">Role<select required value={form.role_id} onChange={(e) => setForm({ ...form, role_id: e.target.value })} className="mt-1.5 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-200 outline-none"><option value="">Select staff role</option>{assignableRoles.map((role) => <option key={role.id} value={role.id}>{role.name}</option>)}</select></label>
          <label className="text-sm text-slate-300">Reason<input required minLength={3} maxLength={500} value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} placeholder="Why is this admin being created?" className="mt-1.5 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-slate-200 outline-none" /></label>
        </div>
        <div className="mt-6 flex justify-end gap-3"><button type="button" onClick={() => setShowCreate(false)} className="rounded-lg border border-slate-700 px-4 py-2.5 text-sm text-slate-300">Cancel</button><button disabled={creating} type="submit" className="rounded-lg bg-cyan-500 px-4 py-2.5 text-sm font-bold text-slate-950 disabled:opacity-50">{creating ? "Creating..." : "Create Admin"}</button></div>
      </form>
    </div>}

    <div className="grid gap-6 xl:grid-cols-[1.25fr_1fr]">
      <section className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5">
        <div className="flex items-center justify-between"><div><h3 className="font-semibold">Administrator accounts</h3><p className="mt-1 text-xs text-slate-500">Role changes are audited. SUPER_ADMIN cannot be reassigned here.</p></div><button onClick={() => void load()} className="rounded-lg border border-slate-700 px-3 py-2 text-xs font-semibold text-slate-300">Refresh</button></div>
        <div className="mt-5 overflow-x-auto"><table className="w-full min-w-[700px] text-left text-sm"><thead className="border-b border-slate-800 text-xs uppercase tracking-wider text-slate-500"><tr><th className="pb-3">Administrator</th><th className="pb-3">Status</th><th className="pb-3">Role</th><th className="pb-3 text-right">Action</th></tr></thead><tbody>{loading ? <tr><td colSpan={4} className="py-12 text-center text-slate-500">Loading RBAC...</td></tr> : admins.map((admin) => <tr key={admin.id} className="border-b border-slate-800/70 last:border-0"><td className="py-4"><div className="font-semibold text-slate-200">{admin.full_name}</div><div className="mt-1 text-xs text-slate-500">{admin.email}</div></td><td className="py-4"><span className={admin.is_active && !admin.is_locked ? "rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs text-emerald-300" : "rounded-full bg-red-500/10 px-2.5 py-1 text-xs text-red-300"}>{admin.is_locked ? "Locked" : admin.is_active ? "Active" : "Inactive"}</span></td><td className="py-4">{admin.roles.includes("SUPER_ADMIN") ? <span className="rounded-full bg-amber-500/10 px-2.5 py-1 text-xs font-semibold text-amber-300">SUPER_ADMIN</span> : <select value={selected[admin.id] || ""} onChange={(e) => setSelected((v) => ({ ...v, [admin.id]: e.target.value }))} className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-300"><option value="">Select role</option>{assignableRoles.map((role) => <option key={role.id} value={role.name}>{role.name}</option>)}</select>}</td><td className="py-4 text-right">{admin.roles.includes("SUPER_ADMIN") ? <span className="text-xs text-slate-600">Protected</span> : <button disabled={!selected[admin.id] || saving === admin.id} onClick={() => void saveRole(admin)} className="rounded-lg bg-cyan-500 px-3 py-2 text-xs font-bold text-slate-950 disabled:opacity-40">{saving === admin.id ? "Saving..." : "Save"}</button>}</td></tr>)}</tbody></table></div>
      </section>
      <section className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5"><h3 className="font-semibold">Role matrix</h3><p className="mt-1 text-xs text-slate-500">{permissions.length} permissions across {roles.length} seeded roles.</p><div className="mt-5 space-y-3">{roles.map((role) => <details key={role.id} className="rounded-xl border border-slate-800 bg-slate-900/40 p-4"><summary className="cursor-pointer list-none"><div className="flex items-center justify-between"><span className="font-medium text-slate-200">{role.name}</span><span className="text-xs text-slate-500">{role.user_count} users · {role.permissions.length} permissions</span></div><div className="mt-1 text-xs text-slate-500">{role.description}</div></summary><div className="mt-4 flex flex-wrap gap-2">{role.permissions.map((permission) => <span key={permission.id} title={permission.description || ""} className="rounded-full border border-slate-700 bg-slate-950 px-2.5 py-1 text-[11px] text-slate-400">{permission.name}</span>)}</div></details>)}</div></section>
    </div>
  </div>;
}
