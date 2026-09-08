"use client";

import { useState } from "react";
import DocumentUploadCard from "./DocumentUploadCard";
import type { KYCDocument } from "@/types/kyc";

export default function DocumentUploadSection() {
  const [documents, setDocuments] = useState<
    Record<string, KYCDocument | undefined>
  >({});

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-white">
          Identity Documents
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Upload the documents required for KYC verification.
        </p>
      </div>

      <DocumentUploadCard
        label="PAN Card"
        type="pan"
        document={documents.PAN}
        onUploaded={(doc) =>
          setDocuments((prev) => ({
            ...prev,
            PAN: doc,
          }))
        }
      />

      <DocumentUploadCard
        label="Aadhaar Front"
        type="aadhaar-front"
        document={documents.AADHAAR_FRONT}
        onUploaded={(doc) =>
          setDocuments((prev) => ({
            ...prev,
            AADHAAR_FRONT: doc,
          }))
        }
      />

      <DocumentUploadCard
        label="Aadhaar Back"
        type="aadhaar-back"
        document={documents.AADHAAR_BACK}
        onUploaded={(doc) =>
          setDocuments((prev) => ({
            ...prev,
            AADHAAR_BACK: doc,
          }))
        }
      />

      <DocumentUploadCard
        label="Live Selfie"
        type="selfie"
        document={documents.SELFIE}
        onUploaded={(doc) =>
          setDocuments((prev) => ({
            ...prev,
            SELFIE: doc,
          }))
        }
      />
    </section>
  );
}