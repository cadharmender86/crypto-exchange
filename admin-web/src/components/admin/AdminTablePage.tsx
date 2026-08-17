import Link from "next/link";

const config: Record<string, { title: string; description: string; columns: string[]; rows: string[][] }> = {
  users: { title: "User management", description: "Search, review and control customer accounts.", columns: ["User", "Status", "KYC", "Joined", "Action"], rows: [["user_10482", "Active", "Verified", "15 Aug 2026", "View"], ["user_09731", "Active", "Pending", "14 Aug 2026", "View"], ["user_08842", "Suspended", "Verified", "12 Aug 2026", "Review"]] },
  kyc: { title: "KYC management", description: "Review verification submissions and compliance status.", columns: ["Applicant", "Tier", "Submitted", "Risk", "Action"], rows: [["user_10482", "Full KYC", "2 min ago", "Low", "Review"], ["user_09731", "Full KYC", "18 min ago", "Medium", "Review"], ["user_08621", "Basic", "1 hr ago", "Low", "Review"]] },
  deposits: { title: "Deposits", description: "Monitor INR and crypto deposit activity.", columns: ["Reference", "User", "Asset", "Amount", "Status"], rows: [["DEP-89231", "user_10291", "INR", "₹50,000", "Confirmed"], ["DEP-89230", "user_10482", "USDT", "1,250", "Pending"], ["DEP-89229", "user_09312", "BTC", "0.042", "Confirmed"]] },
  withdrawals: { title: "Withdrawals", description: "Review and process customer withdrawal requests.", columns: ["Reference", "User", "Asset", "Amount", "Status"], rows: [["WD-78120", "user_09731", "INR", "₹85,000", "Pending"], ["WD-78119", "user_08842", "USDT", "800", "Approved"], ["WD-78118", "user_07321", "BTC", "0.018", "Processing"]] },
  orders: { title: "Orders", description: "Inspect customer buy and sell orders.", columns: ["Order", "User", "Pair", "Side", "Status"], rows: [["ORD-55281", "user_10482", "BTC/INR", "BUY", "Filled"], ["ORD-55280", "user_09731", "ETH/INR", "SELL", "Open"], ["ORD-55279", "user_08312", "USDT/INR", "BUY", "Filled"]] },
  ledger: { title: "Ledger", description: "Read-only financial ledger and balance movements.", columns: ["Entry", "User", "Asset", "Amount", "Type"], rows: [["LED-99012", "user_10482", "INR", "₹25,000", "Trade"], ["LED-99011", "user_09731", "USDT", "500", "Deposit"], ["LED-99010", "user_08312", "BTC", "0.012", "Withdrawal"]] },
  audit: { title: "Audit log", description: "Immutable administrative activity trail.", columns: ["Time", "Admin", "Action", "Target", "Result"], rows: [["23:51", "super_admin", "KYC review", "user_10482", "Success"], ["23:42", "ops_admin_02", "User suspend", "user_08842", "Success"], ["23:18", "finance_admin", "Withdrawal approve", "WD-78119", "Success"]] },
  settings: { title: "Admin settings", description: "Configure operational controls and administrator access.", columns: ["Setting", "Current value", "Scope", "Status", "Action"], rows: [["Withdrawal approval", "2-person review", "Finance", "Enabled", "Manage"], ["KYC auto-approval", "Disabled", "Compliance", "Active", "Manage"], ["Session timeout", "30 minutes", "Security", "Active", "Manage"]] },
};

export default function AdminTablePage({ section }: { section: keyof typeof config }) {
  const data = config[section];
  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div><h2 className="text-2xl font-bold tracking-tight">{data.title}</h2><p className="mt-2 text-sm text-slate-500">{data.description}</p></div>
      <div className="rounded-2xl border border-slate-800 bg-[#0d1422] p-5">
        <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between"><input placeholder={`Search ${section}...`} className="w-full max-w-md rounded-xl border border-slate-700 bg-slate-950/50 px-4 py-2.5 text-sm outline-none placeholder:text-slate-600 focus:border-cyan-500" /><button className="rounded-xl border border-slate-700 px-4 py-2.5 text-sm font-semibold text-slate-300 hover:border-slate-500">Export</button></div>
        <div className="overflow-x-auto"><table className="w-full min-w-[720px] text-left text-sm"><thead className="border-b border-slate-800 text-xs uppercase tracking-wider text-slate-500"><tr>{data.columns.map((column) => <th key={column} className="pb-3 pr-5">{column}</th>)}</tr></thead><tbody>{data.rows.map((row) => <tr key={row[0]} className="border-b border-slate-800/70 last:border-0">{row.map((cell, index) => <td key={`${row[0]}-${index}`} className={`py-4 pr-5 ${index === 0 ? "font-semibold text-slate-200" : "text-slate-400"}`}>{cell}</td>)}</tr>)}</tbody></table></div>
      </div>
      {section === "withdrawals" && <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-amber-200">Approval actions will be wired to the completed withdrawal management APIs in the next integration step.</div>}
      {section === "kyc" && <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4 text-sm text-cyan-200">KYC review UI is ready for API integration with the existing admin KYC endpoints.</div>}
      {section === "users" && <Link href="/admin/kyc" className="inline-flex rounded-xl bg-cyan-500 px-4 py-2.5 text-sm font-bold text-slate-950">Open KYC queue →</Link>}
    </div>
  );
}
