"use client";

import { useState } from "react";
import { uploadKYCDocument } from "@/services/kyc";
import type { KYCDocument } from "@/types/kyc";

type Props = {
  label: string;
  type: "pan" | "aadhaar-front" | "aadhaar-back" | "selfie";
  document?: KYCDocument;
  onUploaded: (doc: KYCDocument) => void;
};

export default function DocumentUploadCard({
  label,
  type,
  document,
  onUploaded,
}: Props) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  async function handleFileChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0];

    if (!file) return;

    setUploading(true);
    setError("");

    try {
      const response = await uploadKYCDocument(type, file);

      onUploaded(response.document);
    } catch (err) {
      console.error(err);
      setError("Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0d141c] p-5">
      <div className="flex items-center justify-between">

        <div>
          <h3 className="font-semibold text-white">{label}</h3>

          <p className="mt-1 text-sm text-slate-400">
            JPG, PNG or PDF • Max 5 MB
          </p>
        </div>

        {document && (
          <span className="rounded-full bg-yellow-500/20 px-3 py-1 text-xs text-yellow-400">
            {document.status}
          </span>
        )}

      </div>

      <div className="mt-5">
        <input
          type="file"
          accept=".jpg,.jpeg,.png,.pdf"
          onChange={handleFileChange}
          className="block w-full text-sm text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-blue-600 file:px-4 file:py-2 file:text-white hover:file:bg-blue-700"
        />
      </div>

      {uploading && (
        <p className="mt-3 text-sm text-blue-400">
          Uploading...
        </p>
      )}

      {document && (
        <div className="mt-3 rounded-lg bg-slate-800 p-3">
          <p className="text-sm text-green-400">
            Uploaded successfully
          </p>

          <p className="mt-1 text-xs text-slate-300">
            {document.file_name}
          </p>
        </div>
      )}

      {error && (
        <p className="mt-3 text-sm text-red-400">{error}</p>
      )}
    </div>
  );
}