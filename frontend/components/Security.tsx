export default function Security() {
  return (
    <section className="bg-[#070b14] py-24">
      <div className="mx-auto grid max-w-7xl gap-12 px-4 lg:grid-cols-2 lg:px-8">

        <div>
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
            Security
          </p>

          <h2 className="mt-4 text-4xl font-bold text-white">
            Security built into every layer
          </h2>

          <p className="mt-5 max-w-xl leading-8 text-gray-400">
            Your exchange infrastructure should be designed with
            security, account protection, transaction monitoring and
            controlled asset custody from the beginning.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">

          {[
            "Two-factor authentication",
            "Withdrawal protection",
            "Cold wallet architecture",
            "Transaction monitoring",
            "Encrypted infrastructure",
            "24/7 system monitoring",
          ].map((item) => (
            <div
              key={item}
              className="rounded-xl border border-white/10 bg-white/[0.03] p-5"
            >
              <div className="mb-3 text-blue-400">
                ✓
              </div>

              <p className="font-medium text-white">
                {item}
              </p>
            </div>
          ))}

        </div>

      </div>
    </section>
  );
}