import Link from "next/link";

export default function OtcPage() {
  return (
    <main className="min-h-screen bg-[#070b14] px-4 py-10 text-white lg:px-8">
      <div className="mx-auto max-w-5xl">
        <Link href="/" className="text-sm text-blue-400">← BitNova</Link>
        <section className="mt-10 rounded-3xl border border-white/10 bg-white/[0.03] p-8 lg:p-12">
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">BitNova OTC</p>
          <h1 className="mt-4 text-4xl font-bold">Large crypto trades, handled directly</h1>
          <p className="mt-5 max-w-2xl leading-7 text-gray-400">
            OTC execution is prepared as a customer-facing workflow. Pricing and settlement will be connected to the backend OTC service when that trading phase is enabled.
          </p>
          <Link href="/login" className="mt-8 inline-block rounded-xl bg-blue-500 px-6 py-3 font-semibold hover:bg-blue-600">
            Sign in to continue
          </Link>
        </section>
      </div>
    </main>
  );
}
