"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
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
  const [creating, setCreating] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [form, setForm] = useState({ email: "", full_name: "", password: "", role_id: "", reason: "" });
  const [roleConfirmation, setRoleConfirmation] = useState<{ admin: Admin; currentRole: string; newRole: string; newRoleId: string } | null>(null);
  const [roleConfirmationStep, setRoleConfirmationStep] = useState<1 | 2>(1);
  const [roleReason, setRoleReason] = useState("");

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

  function cancelRoleConfirmation() {
    setRoleConfirmation(null);
    setRoleConfirmationStep(1);
    setRoleReason("");
  }

  function openRoleConfirmation(admin: Admin) {
    const newRoleName = selected[admin.id];
    const newRole = roles.find((item) => item.name === newRoleName);
    if (!newRole) return;
    const currentRole = admin.roles[0] || "UNASSIGNED";
    if (currentRole === newRole.name) return;
    setError("");
    setNotice("");
    setRoleReason("");
    setRoleConfirmation({ admin, currentRole, newRole: newRole.name, newRoleId: newRole.id });
    setRoleConfirmationStep(1);
  }

  async function confirmRoleChange() {
    if (!roleConfirmation || roleReason.trim().length < 3) return;
    const { admin, newRole, newRoleId } = roleConfirmation;
    setSaving(admin.id); setError(""); setNotice("");
    try {
      const response = await adminFetch(`/api/v1/admin/rbac/admins/${admin.id}/roles`, {
        method: "PATCH", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role_ids: [newRoleId], reason: roleReason.trim() }),
      });
      const data = (await response.json()) as { roles: string[]; detail?: string };
      if (!response.ok) throw new Error(data.detail || "Unable to update role");
      setAdmins((items) => items.map((item) => item.id === admin.id ? { ...item, roles: data.roles } : item));
      setSelected((items) => ({ ...items, [admin.id]: data.roles[0] || newRole }));
      setNotice(`Role changed for ${admin.email}: ${roleConfirmation.currentRole} → ${newRole}.`);
      cancelRoleConfirmation();
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to update role"); }
    finally { setSaving(null); }
  }

  async function createAdmin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const email = form.email.trim();
    const fullName = form.full_name.trim();
    const password = form.password;
    const reason = form.reason.trim();

    if (!fullName || !email || !password || !form.role_id || !reason) {
      setError("All fields are mandatory.");
      return;
    }
    if (fullName.length < 2) {
      setError("Full name must contain at least 2 characters.");
      return;
    }
    if (password.length < 12) {
      setError("Initial password must contain at least 12 characters.");
      return;
    }
    if (reason.length < 3) {
      setError("Reason must contain at least 3 characters.");
      return;
    }

    setCreating(true); setError(""); setNotice("");
    try {
      const response = await adminFetch("/api/v1/admin/rbac/admins", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, full_name: fullName, password, role_id: form.role_id, reason }),
      });
      const data = (await response.json()) as Admin & { detail?: string };
      if (!response.ok) throw new Error(data.detail || "Unable to create administrator");
      setAdmins((items) => [data, ...items]);
      setSelected((items) => ({ ...items, [data.id]: data.roles[0] || "" }));
      setForm({ email: "", full_name: "", password: "", role_id: "", reason: "" });
      setShowPassword(false);
      setShowCreateForm(false);
      setNotice(`Administrator ${data.email} created successfully.`);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to create administrator"); }
    finally { setCreating(false); }
  }

  const canSubmit = form.full_name.trim().length >= 2 && form.email.trim().length > 0 && form.password.length >= 12 && !!form.role_id && form.reason.trim().length >= 3;

  return <div className="mx-auto max-w-7xl space-y-6">
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div><h2 className="text-2xl font-bold tracking-tight">Admin RBAC</h2><p className="mt-2 text-sm text-slate-500">Manage administrator accounts, roles and permissions.</p></div>
      <button onClick={() => { setShowCreateForm(true); setError(""); setNotice(""); }} className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-bold text-slate-950">+ Create Administrator</button>
    </div>
    {error && <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-3 text-sm text-red-300">{error}</div>}
    {notice && <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3 text-sm text-emerald-300">{notice}</div>}

    {roleConfirmation && (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm">
        <div className="w-full max-w-lg rounded-2xl border border-slate-700 bg-[#0d1422] p-6 shadow-2xl">
          {roleConfirmationStep === 1 ? (
            <>
              <h3 className="text-lg font-bold text-white">Confirm role change</h3>
              <p className="mt-2 text-sm text-slate-400">Review the proposed administrator role change before continuing.</p>
              <div className="mt-5 rounded-xl border border-slate-700 bg-slate-950/60 p-4">
                <div className="text-xs uppercase tracking-wider text-slate-500">Administrator</div>
                <div className="mt-1 font-semibold text-white">{roleConfirmation.admin.full_name}</div>
                <div className="text-xs text-slate-500">{roleConfirmation.admin.email}</div>
                <div className="mt-5 grid grid-cols-[1fr_auto_1fr] items-center gap-3">
                  <div><div className="text-xs text-slate-500">Current role</div><div className="mt-1 font-semibold text-slate-300">{roleConfirmation.currentRole}</div></div>
                  <div className="text-lg text-cyan-400">→</div>
                  <div><div className="text-xs text-slate-500">New role</div><div className="mt-1 font-bold text-cyan-300">{roleConfirmation.newRole}</div></div>
                </div>
              </div>
              <div className="mt-5 flex justify-end gap-3"><button type="button" onClick={cancelRoleConfirmation} className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-300">Cancel</button><button type="button" onClick={() => setRoleConfirmationStep(2)} className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-bold text-slate-950">Continue</button></div>
            </>
          ) : (
            <>
              <h3 className="text-lg font-bold text-white">Final confirmation</h3>
              <p className="mt-2 text-sm text-slate-400">This action will immediately change the administrator's role and access permissions.</p>
              <div className="mt-4 rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 text-sm">
                <div className="font-semibold text-amber-300">{roleConfirmation.admin.email}</div>
                <div className="mt-2 text-slate-400">Current: <span className="font-semibold text-slate-200">{roleConfirmation.currentRole}</span></div>
                <div className="mt-1 text-slate-400">New role: <span className="font-bold text-cyan-300">{roleConfirmation.newRole}</span></div>
              </div>
              <label className="mt-4 block text-xs text-slate-400">Reason <span className="text-red-400">*</span><input autoFocus value={roleReason} onChange={(e) => setRoleReason(e.target.value)} placeholder="Why is this role change required?" className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-cyan-500" /></label>
              <div className="mt-5 flex justify-end gap-3"><button type="button" onClick={() => setRoleConfirmationStep(1)} disabled={saving !== null} className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-300">Back</button><button type="button" onClick={cancelRoleConfirmation} disabled={saving !== null} className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-300">Cancel</button><button type="button" onClick={() => void confirmRoleChange()} disabled={roleReason.trim().length < 3 || saving !== null} className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-40">{saving ? "Changing..." : "Confirm Role Change"}</button></div>
            </>
          )}
        </div>
      </div>
    )}

    {showCreateForm && (
      <section className="rounded-2xl border border-cyan-500/20 bg-[#0d1422] p-5">
        <div className="mb-4 flex items-center justify-between"><div><h3 className="font-semibold">Create Administrator</h3><p className="mt-1 text-xs text-slate-500">Only SUPER_ADMIN can create administrators. You may create another SUPER_ADMIN or a restricted staff administrator.</p></div><button type="button" onClick={() => { setShowCreateForm(false); setShowPassword(false); setForm({ email: "", full_name: "", password: "", role_id: "", reason: "" }); }} className="text-xs text-slate-500 hover:text-white">Cancel</button></div>
        <form onSubmit={createAdmin} className="grid gap-4 md:grid-cols-2">
          <label className="text-xs text-slate-400">Full name <span className="text-red-400">*</span><input required aria-required="true" minLength={2} value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-cyan-500" /></label>
          <label className="text-xs text-slate-400">Email <span className="text-red-400">*</span><input required aria-required="true" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-cyan-500" /></label>
          <label className="text-xs text-slate-400">Initial password <span className="text-red-400">*</span><div className="relative mt-1"><input required aria-required="true" minLength={12} type={showPassword ? "text" : "password"} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 pr-16 text-sm text-white outline-none focus:border-cyan-500" /><button type="button" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword((value) => !value)} className="absolute right-2 top-1/2 -translate-y-1/2 rounded px-2 py-1 text-xs font-semibold text-slate-400 hover:text-white">{showPassword ? "Hide" : "Show"}</button></div></label>
          <label className="text-xs text-slate-400">Role <span className="text-red-400">*</span><select required aria-required="true" value={form.role_id} onChange={(e) => setForm({ ...form, role_id: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-cyan-500"><option value="">Select role</option>{roles.filter((r) => r.is_active).map((role) => <option key={role.id} value={role.id}>{role.name}</option>)}</select></label>
          <label className="text-xs text-slate-400 md:col-span-2">Reason <span className="text-red-400">*</span><input required aria-required="true" minLength={3} value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} placeholder="Why is this administrator being created?" className="mt-1 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-cyan-500" /></label>
          <div className="md:col-span-2 flex justify-end"><button type="submit" disabled={!canSubmit || creating} className="rounded-lg bg-cyan-500 px-5 py-2.5 text-sm font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-40">{creating ? "Submitting..." : "Submit"}</button></div>
        </form>
      </section>
    )}

    <div className="grid gap-6 xl:grid-cols-[1.25fr_1fr]">
      <section className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5">
        <div className="flex items-center justify-between"><div><h3 className="font-semibold">Administrator accounts</h3><p className="mt-1 text-xs text-slate-500">Role changes are audited and require SUPER_ADMIN.</p></div><button onClick={() => void load()} className="rounded-lg border border-slate-700 px-3 py-2 text-xs font-semibold text-slate-300">Refresh</button></div>
        <div className="mt-5 overflow-x-auto"><table className="w-full min-w-[700px] text-left text-sm"><thead className="border-b border-slate-800 text-xs uppercase tracking-wider text-slate-500"><tr><th className="pb-3">Administrator</th><th className="pb-3">Status</th><th className="pb-3">Role</th><th className="pb-3 text-right">Action</th></tr></thead><tbody>{loading ? <tr><td colSpan={4} className="py-12 text-center text-slate-500">Loading RBAC...</td></tr> : admins.map((admin) => <tr key={admin.id} className="border-b border-slate-800/70 last:border-0"><td className="py-4"><div className="font-semibold text-slate-200">{admin.full_name}</div><div className="mt-1 text-xs text-slate-500">{admin.email}</div></td><td className="py-4"><span className={admin.is_active && !admin.is_locked ? "rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs text-emerald-300" : "rounded-full bg-red-500/10 px-2.5 py-1 text-xs text-red-300"}>{admin.is_locked ? "Locked" : admin.is_active ? "Active" : "Inactive"}</span></td><td className="py-4"><select value={selected[admin.id] || ""} onChange={(e) => setSelected((v) => ({ ...v, [admin.id]: e.target.value }))} className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-300"><option value="">Select role</option>{roles.filter((r) => r.is_active).map((role) => <option key={role.id} value={role.name}>{role.name}</option>)}</select></td><td className="py-4 text-right"><button disabled={!selected[admin.id] || selected[admin.id] === (admin.roles[0] || "") || saving === admin.id} onClick={() => openRoleConfirmation(admin)} className="rounded-lg bg-cyan-500 px-3 py-2 text-xs font-bold text-slate-950 disabled:cursor-not-allowed disabled:opacity-40">{saving === admin.id ? "Changing..." : "Change Role"}</button></td></tr>)}</tbody></table></div>
      </section>
      <section className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5"><h3 className="font-semibold">Role matrix</h3><p className="mt-1 text-xs text-slate-500">{permissions.length} permissions across {roles.length} seeded roles.</p><div className="mt-5 space-y-3">{roles.map((role) => <details key={role.id} className="rounded-xl border border-slate-800 bg-slate-900/40 p-4"><summary className="cursor-pointer list-none"><div className="flex items-center justify-between"><span className="font-medium text-slate-200">{role.name}</span><span className="text-xs text-slate-500">{role.user_count} users · {role.permissions.length} permissions</span></div><div className="mt-1 text-xs text-slate-500">{role.description}</div></summary><div className="mt-4 flex flex-wrap gap-2">{role.permissions.map((permission) => <span key={permission.id} title={permission.description || ""} className="rounded-full border border-slate-700 bg-slate-950 px-2.5 py-1 text-[11px] text-slate-400">{permission.name}</span>)}</div></details>)}</div></section>
    </div>
  </div>;
}
