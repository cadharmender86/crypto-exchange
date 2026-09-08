export default function KYCStatusCard() {
  return (
    <div className="rounded-xl border border-slate-800 bg-[#0d141c] p-5">
      <div className="flex items-center justify-between">

        <div>
          <p className="text-sm text-slate-400">
            Verification Status
          </p>

          <h2 className="mt-1 text-xl font-bold text-yellow-400">
            Draft
          </h2>
        </div>

        <span className="rounded-full bg-yellow-500/15 px-3 py-1 text-xs font-semibold text-yellow-400">
          DRAFT
        </span>

      </div>

      <p className="mt-4 text-sm text-slate-400">
        Fill your personal information and upload required documents.
      </p>
    </div>
  );
}