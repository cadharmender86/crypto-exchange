import Link from "next/link";
import QuickOrders from "@/components/dashboard/QuickOrders";

const quickActions = [
  { href: "/buy-sell", label: "Buy / Sell", description: "Trade crypto with INR" },
  { href: "/markets", label: "Markets", description: "View available markets" },
  { href: "/kyc", label: "Complete KYC", description: "Verify your account" },
  { href: "/otc", label: "OTC Trading", description: "Request an OTC trade" },
];

const portfolioItems = [
  { asset: "INR", value: "—", note: "Available balance" },
  { asset: "BTC", value: "—", note: "Wallet balance" },
  { asset: "ETH", value: "—", note: "Wallet balance" },
];

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-[#070b14] px-4 py-8 text-white sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm text-blue-400">BitNova Customer Portal</p>
            <h1 className="mt-1 text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="mt-2 text-sm text-gray-400">
              Manage your wallet, trading activity and account verification from one place.
            </p>
          </div>
          <div className="flex gap-3">
            <Link href="/buy-sell" className="rounded-xl bg-blue-500 px-5 py-3 text-sm font-semibold hover:bg-blue-600">
              Trade now
            </Link>
            <Link href="/kyc" className="rounded-xl border border-white/10 px-5 py-3 text-sm font-semibold hover:bg-white/5">
              KYC
            </Link>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          {portfolioItems.map((item) => (
            <div key={item.asset} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">{item.asset}</span>
                <span className="rounded-full bg-white/5 px-2.5 py-1 text-xs text-gray-400">Live data</span>
              </div>
              <p className="mt-5 text-2xl font-semibold">{item.value}</p>
              <p className="mt-1 text-xs text-gray-500">{item.note}</p>
            </div>
          ))}
        </section>

        <section className="mt-8">
          <div className="mb-4">
            <h2 className="text-xl font-semibold">Quick actions</h2>
            <p className="mt-1 text-sm text-gray-400">Jump directly to the most-used customer workflows.</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {quickActions.map((action) => (
              <Link key={action.href} href={action.href} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 transition hover:border-blue-500/40 hover:bg-white/[0.05]">
                <h3 className="font-semibold">{action.label}</h3>
                <p className="mt-2 text-sm text-gray-400">{action.description}</p>
                <span className="mt-4 inline-block text-sm text-blue-400">Open →</span>
              </Link>
            ))}
          </div>
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[1.5fr_1fr]">
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h2 className="font-semibold">Account status</h2>
                <p className="mt-1 text-sm text-gray-400">Keep your account ready for trading and withdrawals.</p>
              </div>
              <Link href="/kyc" className="text-sm text-blue-400">View KYC →</Link>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <Status label="Email" value="Verified" />
              <Status label="KYC" value="Review" />
              <Status label="Security" value="Protected" />
            </div>
          </div>

          <QuickOrders />
        </section>
      </div>
    </main>
  );
}

function Status({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-black/20 p-4">
      <p className="text-xs uppercase tracking-wide text-gray-500">{label}</p>
      <p className="mt-2 text-sm font-medium text-gray-200">{value}</p>
    </div>
  );
}
