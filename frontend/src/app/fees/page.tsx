import Link from "next/link";

const fees = [
  ["Spot trading", "Coming with trading engine"],
  ["Deposits", "Network-dependent"],
  ["Withdrawals", "Asset/network-dependent"],
  ["OTC", "Quoted per transaction"],
];

export default function FeesPage() {
  return (
    <main className="min-h-screen bg-[#070b14] px-4 py-10 text-white lg:px-8">
      <div className="mx-auto max-w-5xl">
        <Link href="/" className="text-sm text-blue-400">← BitNova</Link>
        <h1 className="mt-4 text-4xl font-bold">Fees</h1>
        <p className="mt-2 text-gray-400">A transparent fee surface for the exchange.</p>
        <div className="mt-8 overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03]">
          {fees.map(([name, value]) => (
            <div key={name} className="flex flex-wrap justify-between gap-4 border-b border-white/10 p-5 last:border-b-0">
              <span className="font-medium">{name}</span>
              <span className="text-gray-400">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
