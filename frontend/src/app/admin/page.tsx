import Link from "next/link";

const stats = [
  ["Total users", "12,482", "+4.8%", "text-cyan-300"],
  ["Pending KYC", "186", "23 high priority", "text-amber-300"],
  ["Pending withdrawals", "42", "₹18.4L value", "text-orange-300"],
  ["24h trading volume", "₹3.82Cr", "+12.6%", "text-emerald-300"],
];

const activities = [
  ["KYC submitted", "user_10482", "2 min ago", "Review"],
  ["Withdrawal requested", "user_09731", "8 min ago", "Open"],
  ["User suspended", "user_08842", "14 min ago", "View"],
  ["Deposit confirmed", "user_10291", "21 min ago", "Open"],
  ["Admin role changed", "ops_admin_02", "38 min ago", "View"],
];

export default function AdminDashboard() {
  return (
    <div className="mx-auto max-w-7xl space-y-7">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-sm text-slate-400">Good evening, Super Admin</p>
          <h2 className="mt-1 text-2xl font-bold tracking-tight">Exchange overview</h2>
          <p className="mt-2 text-sm text-slate-500">Monitor users, compliance and financial operations from one console.</p>
        </div>
        <Link href="/admin/kyc" className="rounded-xl bg-cyan-500 px-4 py-2.5 text-sm font-bold text-slate-950 hover:bg-cyan-400">Review pending KYC</Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map(([label, value, trend, tone]) => (
          <div key={label} className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5 shadow-xl shadow-black/10">
            <div className="text-sm text-slate-500">{label}</div>
            <div className={`mt-3 text-2xl font-bold ${tone}`}>{value}</div>
            <div className="mt-2 text-xs text-slate-500">{trend}</div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
        <div className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5">
          <div className="flex items-center justify-between">
            <div><h3 className="font-semibold">Operational activity</h3><p className="mt-1 text-xs text-slate-500">Latest admin-relevant events</p></div>
            <Link href="/admin/audit" className="text-xs font-semibold text-cyan-400 hover:text-cyan-300">View audit log →</Link>
          </div>
          <div className="mt-5 overflow-x-auto">
            <table className="w-full min-w-[620px] text-left text-sm">
              <thead className="border-b border-slate-800 text-xs uppercase tracking-wider text-slate-500"><tr><th className="pb-3">Event</th><th className="pb-3">Actor / User</th><th className="pb-3">Time</th><th className="pb-3 text-right">Action</th></tr></thead>
              <tbody>{activities.map(([event, actor, time, action]) => <tr key={`${event}-${actor}`} className="border-b border-slate-800/70 last:border-0"><td className="py-4 font-medium text-slate-200">{event}</td><td className="py-4 text-slate-400">{actor}</td><td className="py-4 text-slate-500">{time}</td><td className="py-4 text-right"><button className="text-xs font-semibold text-cyan-400 hover:text-cyan-300">{action}</button></td></tr>)}</tbody>
            </table>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5">
          <h3 className="font-semibold">Compliance queue</h3>
          <p className="mt-1 text-xs text-slate-500">Items requiring operator attention</p>
          <div className="mt-5 space-y-3">
            {["KYC verification", "Withdrawal approvals", "Suspended accounts", "AML review flags"].map((item, i) => (
              <Link key={item} href={i === 0 ? "/admin/kyc" : "/admin/audit"} className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/50 p-4 hover:border-slate-700">
                <div><div className="text-sm font-medium">{item}</div><div className="mt-1 text-xs text-slate-500">{[186, 42, 9, 7][i]} open items</div></div>
                <span className="text-slate-500">→</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
