"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { ApiError, apiFetch, getAccessToken } from "@/lib/api";

type KYCRecord = {
  id: string;
  user_id: string;
  status: string;
  document_type: string | null;
  document_reference: string | null;
  submitted_at: string | null;
  reviewed_at: string | null;
  rejection_reason: string | null;
  created_at: string;
  updated_at: string;
};

type KYCSubmitRequest = {
  document_type: string;
  document_reference: string;
  extra_data?: Record<string, string>;
};

const statusCopy: Record<string, string> = {
  PENDING: "Pending review",
  UNDER_REVIEW: "Under review",
  APPROVED: "Verified",
  REJECTED: "Rejected",
  REQUIRES_REVERIFICATION: "Re-verification required",
};

function statusClass(status: string) {
  if (status === "APPROVED") return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  if (status === "REJECTED") return "border-red-500/30 bg-red-500/10 text-red-300";
  if (status === "UNDER_REVIEW") return "border-amber-500/30 bg-amber-500/10 text-amber-300";
  return "border-blue-500/30 bg-blue-500/10 text-blue-300";
}

export default function KYCPage() {
  const [record, setRecord] = useState<KYCRecord | null>(null);
  const [documentType, setDocumentType] = useState("PAN");
  const [documentReference, setDocumentReference] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const canSubmit = !record || record.status === "REJECTED" || record.status === "REQUIRES_REVERIFICATION";

  async function loadKyc() {
    const token = getAccessToken();
    if (!token) {
      window.location.href = "/login";
      return;
    }

    setLoading(true);
    setError("");
    try {
      const data = await apiFetch<KYCRecord>("/kyc", {}, token);
      setRecord(data);
      setDocumentType(data.document_type || "PAN");
      setDocumentReference(data.document_reference || "");
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setRecord(null);
      } else {
        setError(err instanceof ApiError ? err.message : "Unable to load KYC status.");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadKyc();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setSubmitting(true);

    const token = getAccessToken();
    if (!token) {
      window.location.href = "/login";
      return;
    }

    const payload: KYCSubmitRequest = {
      document_type: documentType.trim(),
      document_reference: documentReference.trim(),
    };

    try {
      const method = record ? "PATCH" : "POST";
      const data = await apiFetch<KYCRecord>("/kyc", {
        method,
        body: JSON.stringify(payload),
      }, token);
      setRecord(data);
      setSuccess("Your KYC application has been submitted successfully.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to submit KYC.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#070b14] px-4 py-10 text-white">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <Link href="/dashboard" className="text-sm text-blue-400 hover:text-blue-300">← Dashboard</Link>
            <h1 className="mt-3 text-3xl font-bold">Identity Verification</h1>
            <p className="mt-2 text-gray-400">Complete KYC to unlock full BitNova account functionality.</p>
          </div>
          {record && (
            <span className={`rounded-full border px-4 py-2 text-sm font-medium ${statusClass(record.status)}`}>
              {statusCopy[record.status] || record.status}
            </span>
          )}
        </div>

        {loading ? (
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-8 text-gray-400">Loading KYC status...</div>
        ) : (
          <div className="grid gap-6 md:grid-cols-[1fr_320px]">
            <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 shadow-xl">
              <h2 className="text-xl font-semibold">KYC application</h2>
              <p className="mt-1 text-sm text-gray-400">Submit your identity document details for verification.</p>

              {!canSubmit && record?.status === "APPROVED" && (
                <div className="mt-6 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-emerald-200">
                  Your identity has been verified. No further action is required.
                </div>
              )}

              {canSubmit && (
                <form onSubmit={handleSubmit} className="mt-6 space-y-5">
                  <label className="block">
                    <span className="text-sm text-gray-300">Document type</span>
                    <select value={documentType} onChange={(e) => setDocumentType(e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-white outline-none focus:border-blue-500">
                      <option value="PAN">PAN</option>
                      <option value="PASSPORT">Passport</option>
                      <option value="DRIVING_LICENSE">Driving License</option>
                      <option value="VOTER_ID">Voter ID</option>
                    </select>
                  </label>

                  <label className="block">
                    <span className="text-sm text-gray-300">Document reference</span>
                    <input required minLength={2} maxLength={255} value={documentReference} onChange={(e) => setDocumentReference(e.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-white outline-none focus:border-blue-500" placeholder="Enter document number" />
                  </label>

                  {error && <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</div>}
                  {success && <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">{success}</div>}

                  <button disabled={submitting} className="w-full rounded-xl bg-blue-500 py-3.5 font-semibold hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-60">
                    {submitting ? "Submitting..." : record ? "Resubmit KYC" : "Submit KYC"}
                  </button>
                </form>
              )}

              {record?.status === "REJECTED" && record.rejection_reason && (
                <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4">
                  <p className="text-sm font-medium text-red-200">Reason for rejection</p>
                  <p className="mt-1 text-sm text-red-300">{record.rejection_reason}</p>
                </div>
              )}
            </section>

            <aside className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
              <h2 className="font-semibold">Verification status</h2>
              <div className="mt-5 space-y-4 text-sm">
                {[
                  ["PENDING", "Application submitted"],
                  ["UNDER_REVIEW", "Admin review"],
                  ["APPROVED", "Identity verified"],
                ].map(([key, label]) => (
                  <div key={key} className="flex items-center gap-3">
                    <span className={`h-2.5 w-2.5 rounded-full ${record?.status === key ? "bg-blue-400" : "bg-white/20"}`} />
                    <span className={record?.status === key ? "text-white" : "text-gray-500"}>{label}</span>
                  </div>
                ))}
              </div>
              <p className="mt-6 text-xs leading-5 text-gray-500">For production, document files should be uploaded to secure storage/KYC-provider infrastructure rather than stored directly in the application database.</p>
            </aside>
          </div>
        )}
      </div>
    </main>
  );
}
