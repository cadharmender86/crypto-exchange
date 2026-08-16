"use client";

import { useCallback, useEffect, useState } from "react";
import { adminFetch } from "@/lib/adminApi";

type Kyc = { id: string; user_id: string; user_email: string; status: string; document_type: string | null; document_reference: string | null; submitted_at: string | null; reviewed_at: string | null; reviewed_by_admin_id: string | null; rejection_reason: string | null; created_at: string; updated_at: string };
type User = { email: string };
type ListResponse = { items: Kyc[]; total: number; page: number; page_size: number };

function formatDate(value: string | null) { return value ? new Date(value).toLocaleString() : "Never"; }
function statusClass(value: string) { const status = value.toUpperCase(); if (status === "APPROVED") return "bg-emerald-500/10 text-emerald-300"; if (status === "REJECTED") return "bg-red-500/10 text-red-300"; if (status === "UNDER_REVIEW") return "bg-cyan-500/10 text-cyan-300"; return "bg-amber-500/10 text-amber-300"; }

export default function UserKycPanel({ userId }: { userId: string }) {
  const [kyc, setKyc] = useState<Kyc | null>(null);
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const userResponse = await adminFetch(`/api/v1/admin/users/${userId}`);
      const userData = (await userResponse.json()) as User & { detail?: string };
      if (!userResponse.ok) throw new Error(userData.detail || "Unable to load user");
      const response = await adminFetch(`/api/v1/admin/kyc?page=1&page_size=25&search=${encodeURIComponent(userData.email)}`);
      const data = (await response.json()) as ListResponse & { detail?: string };
      if (!response.ok) throw new Error(data.detail || "Unable to load KYC record");
      setKyc(data.items.find((item) => item.user_id === userId) || null);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to load KYC record"); }
    finally { setLoading(false); }
  }, [userId]);

  useEffect(() => { void load(); }, [load]);

  async function review(type: "approve" | "reject" | "under-review") {
    if (!kyc) return;
    const reason = window.prompt(type === "reject" ? "Rejection reason:" : "Review reason:");
    if (!reason || reason.trim().length < 3) return;
    setAction(type); setError(""); setNotice("");
    try {
      const response = await adminFetch(`/api/v1/admin/kyc/${kyc.id}/${type}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ reason: reason.trim() }) });
      const data = (await response.json()) as Kyc & { detail?: string };
      if (!response.ok) throw new Error(data.detail || "KYC review failed");
      setKyc(data); setNotice(`KYC ${type === "under-review" ? "marked under review" : `${type}d`} successfully.`);
    } catch (err) { setError(err instanceof Error ? err.message : "KYC review failed"); }
    finally { setAction(null); }
  }

  return (
    <section className="rounded-2xl border border-slate-800 bg-[#0d1422] p-6">
      <div className="flex items-start justify-between gap-4"><div><div className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-400">Compliance</div><h3 className="mt-2 text-base font-semibold text-white">KYC verification</h3><p className="mt-1 text-xs text-slate-500">Verification record and review controls for this customer.</p></div><button onClick={() => void load()} disabled={loading} className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-semibold text-slate-300 disabled:opacity-50">Refresh</button></div>
      {error && <div className="mt-4 rounded-xl border border-red-500/20 bg-red-500/5 p-3 text-xs text-red-300">{error}</div>}
      {notice && <div className="mt-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-3 text-xs text-emerald-300">{notice}</div>}
      {loading ? <div className="py-8 text-sm text-slate-500">Loading KYC record...</div> : !kyc ? <div className="mt-5 rounded-xl border border-dashed border-slate-800 p-7 text-center text-sm text-slate-600">No KYC record found for this user.</div> : <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_auto]"><div className="grid gap-4 sm:grid-cols-2"><div><div className="text-xs text-slate-500">Status</div><div className="mt-2"><span className={`rounded-full px-2.5 py-1 text-xs font-medium ${statusClass(kyc.status)}`}>{kyc.status.replaceAll("_", " ")}</span></div></div><div><div className="text-xs text-slate-500">Document type</div><div className="mt-2 text-sm text-slate-200">{kyc.document_type || "—"}</div></div><div><div className="text-xs text-slate-500">Submitted</div><div className="mt-2 text-sm text-slate-300">{formatDate(kyc.submitted_at)}</div></div><div><div className="text-xs text-slate-500">Reviewed</div><div className="mt-2 text-sm text-slate-300">{formatDate(kyc.reviewed_at)}</div></div><div className="sm:col-span-2"><div className="text-xs text-slate-500">Document reference</div><div className="mt-2 break-all font-mono text-xs text-slate-400">{kyc.document_reference || "—"}</div></div>{kyc.rejection_reason && <div className="sm:col-span-2 rounded-xl border border-red-500/20 bg-red-500/5 p-3 text-xs text-red-300"><span className="font-semibold">Rejection reason:</span> {kyc.rejection_reason}</div>}</div>{!['APPROVED', 'REJECTED'].includes(kyc.status) && <div className="flex flex-row gap-2 lg:flex-col lg:justify-center"><button disabled={!!action} onClick={() => void review("under-review")} className="rounded-lg border border-cyan-500/30 px-3 py-2 text-xs font-semibold text-cyan-300 disabled:opacity-40">{action === "under-review" ? "Saving..." : "Review"}</button><button disabled={!!action} onClick={() => void review("approve")} className="rounded-lg border border-emerald-500/30 px-3 py-2 text-xs font-semibold text-emerald-300 disabled:opacity-40">{action === "approve" ? "Saving..." : "Approve"}</button><button disabled={!!action} onClick={() => void review("reject")} className="rounded-lg border border-red-500/30 px-3 py-2 text-xs font-semibold text-red-300 disabled:opacity-40">{action === "reject" ? "Saving..." : "Reject"}</button></div>}</div>}
    </section>
  );
}
