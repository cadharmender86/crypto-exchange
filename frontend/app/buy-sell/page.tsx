import Link from "next/link";
import BuySell from "@/components/BuySell";

export default function BuySellPage() {
  return (
    <main className="min-h-screen bg-[#070b14] text-white">
      <div className="mx-auto max-w-7xl px-4 pt-8 lg:px-8">
        <Link href="/" className="text-sm text-blue-400">← BitNova</Link>
      </div>
      <BuySell />
      <div className="mx-auto max-w-7xl px-4 pb-16 text-center text-sm text-gray-500 lg:px-8">
        Trading execution will be enabled when the backend order/trading phase is implemented.
      </div>
    </main>
  );
}
