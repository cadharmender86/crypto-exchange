import Link from "next/link";

export default function CTA() {
  return (
    <section className="bg-[#0a0f1b] px-4 py-24">
      <div className="mx-auto max-w-5xl overflow-hidden rounded-3xl border border-blue-400/20 bg-blue-500/[0.08] p-10 text-center md:p-16">

        <h2 className="text-4xl font-bold text-white md:text-5xl">
          Start your crypto journey
        </h2>

        <p className="mx-auto mt-5 max-w-xl text-gray-400">
          Create your account and explore the next generation
          of digital asset trading.
        </p>

        <Link
          href="/register"
          className="mt-8 inline-block rounded-xl bg-blue-500 px-8 py-4 font-semibold text-white hover:bg-blue-600"
        >
          Create Account
        </Link>

      </div>
    </section>
  );
}