import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-8">
      <section className="max-w-3xl w-full space-y-6">
        <p className="text-sm uppercase tracking-widest text-slate-400">BitNova Exchange</p>
        <h1 className="text-4xl font-bold">Customer Web Application</h1>
        <p className="text-slate-300">
          This is the authenticated customer application. The public marketing website
          is maintained separately under <code>landing-web/</code>.
        </p>
        <div className="flex gap-3">
          <Link className="rounded-lg bg-white px-5 py-3 text-slate-950 font-medium" href="/login">
            Login
          </Link>
          <Link className="rounded-lg border border-slate-700 px-5 py-3" href="/dashboard">
            Dashboard
          </Link>
        </div>
      </section>
    </main>
  );
}
