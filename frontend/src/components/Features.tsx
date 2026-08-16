const features = [
  {
    icon: "⚡",
    title: "Fast execution",
    description:
      "Designed for reliable order execution and real-time market updates.",
  },
  {
    icon: "🔐",
    title: "Security first",
    description:
      "Multi-layer security architecture protects accounts and digital assets.",
  },
  {
    icon: "₹",
    title: "INR trading",
    description:
      "Trade digital assets with an experience designed for Indian users.",
  },
  {
    icon: "📊",
    title: "Advanced markets",
    description:
      "Access spot markets, market data and professional trading tools.",
  },
];

export default function Features() {
  return (
    <section className="bg-[#070b14] py-24">
      <div className="mx-auto max-w-7xl px-4 lg:px-8">

        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
            Why BitNova
          </p>

          <h2 className="mt-4 text-4xl font-bold text-white">
            Everything you need to trade
          </h2>

          <p className="mt-5 text-gray-400">
            A modern trading platform built around simplicity,
            security and performance.
          </p>
        </div>

        <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-2xl border border-white/10 bg-white/[0.03] p-7 transition hover:-translate-y-1 hover:bg-white/[0.05]"
            >
              <div className="text-3xl">
                {feature.icon}
              </div>

              <h3 className="mt-5 text-xl font-semibold text-white">
                {feature.title}
              </h3>

              <p className="mt-3 leading-7 text-gray-400">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}