"use client";

import VerificationStepper from "./VerificationStepper";
import KYCStatusCard from "./KYCStatusCard";
import PersonalInfoForm from "./PersonalInfoForm";
import DocumentUploadSection from "./DocumentUploadSection";

export default function KYCWizard() {
  return (
    <section className="min-h-screen bg-[#080d12] text-white">
      <div className="mx-auto max-w-7xl px-6 py-8">

        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">
            KYC Verification
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Complete identity verification to unlock INR deposits,
            crypto withdrawals, futures, and higher trading limits.
          </p>
        </div>

        <KYCStatusCard />

        <div className="mt-6 grid gap-6 xl:grid-cols-[280px_1fr]">

          <VerificationStepper />

          <div className="space-y-6">
            <PersonalInfoForm />

            <DocumentUploadSection />
          </div>

        </div>

      </div>
    </section>
  );
}