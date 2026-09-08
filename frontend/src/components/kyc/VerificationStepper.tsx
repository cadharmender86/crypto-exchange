const steps = [
  "Personal Information",
  "PAN Card",
  "Aadhaar Front",
  "Aadhaar Back",
  "Selfie Verification",
  "Submit KYC",
];

export default function VerificationStepper() {
  return (
    <aside className="rounded-xl border border-slate-800 bg-[#0d141c] p-5">

      <h3 className="mb-5 text-lg font-semibold">
        Verification Steps
      </h3>

      <div className="space-y-5">
        {steps.map((step, index) => (
          <div key={step} className="flex items-start gap-3">

            <div
              className={`mt-1 flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold ${
                index === 0
                  ? "bg-blue-600 text-white"
                  : "bg-slate-700 text-slate-300"
              }`}
            >
              {index + 1}
            </div>

            <div>
              <p
                className={`text-sm ${
                  index === 0
                    ? "text-white font-semibold"
                    : "text-slate-400"
                }`}
              >
                {step}
              </p>
            </div>

          </div>
        ))}
      </div>

    </aside>
  );
}