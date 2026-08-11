import Link from "next/link";

const products = [
  {
    title: "Spot Trading",
    description:
      "Trade crypto pairs with a professional order book and real-time market data.",
    href: "/markets",
  },
  {
    title: "OTC Trading",
    description:
      "Dedicated trading support for high-volume crypto transactions.",
    href: "/otc",
  },
  {
    title: "Crypto SIP",
    description:
      "Build a disciplined crypto investment strategy through recurring purchases.",
    href: "#",
  },
  {
    title: "Crypto Baskets",
    description:
      "Explore diversified collections of digital assets.",
    href: "#",
  },
];

export default function Products() {
  return (
    <section className="bg-[#0a0f1b] py-24">
      <div className="mx-auto max-w-7xl px-4 lg:px-8">

        <div className="flex flex-col justify-between gap-6 md:flex-row md:items-end">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
              Products
            </p>

            <h2 className="mt-4 text-4xl font-bold text-white">
              More ways to use crypto
            </h2>
          </div>
        </div>

        <div className="mt-12 grid gap-5 md:grid-cols-2">
          {products.map((product) => (
            <Link
              href={product.href}
              key={product.title}
              className="group rounded-2xl border border-white/10 bg-white/[0.03] p-8 transition hover:border-blue-400/30 hover:bg-blue-400/[0.04]"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-2xl font-semibold text-white">
                  {product.title}
                </h3>

                <span className="text-xl text-blue-400 transition group-hover:translate-x-1">
                  →
                </span>
              </div>

              <p className="mt-4 max-w-xl leading-7 text-gray-400">
                {product.description}
              </p>
            </Link>
          ))}
        </div>

      </div>
    </section>
  );
}