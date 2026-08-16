import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-[#050810]">
      <div className="mx-auto max-w-7xl px-4 py-14 lg:px-8">

        <div className="grid gap-10 md:grid-cols-4">

          <div>
            <div className="text-xl font-bold text-white">
              Bit<span className="text-blue-400">Nova</span>
            </div>

            <p className="mt-4 max-w-xs text-sm leading-6 text-gray-500">
              A modern digital asset platform designed for
              secure and simple crypto trading.
            </p>
          </div>

          <div>
            <h3 className="font-semibold text-white">
              Products
            </h3>

            <div className="mt-4 space-y-3 text-sm text-gray-500">
              <Link className="block hover:text-white" href="/markets">
                Markets
              </Link>
              <Link className="block hover:text-white" href="/buy-sell">
                Buy Crypto
              </Link>
              <Link className="block hover:text-white" href="/otc">
                OTC
              </Link>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-white">
              Company
            </h3>

            <div className="mt-4 space-y-3 text-sm text-gray-500">
              <Link className="block hover:text-white" href="#">
                About
              </Link>
              <Link className="block hover:text-white" href="#">
                Careers
              </Link>
              <Link className="block hover:text-white" href="#">
                Contact
              </Link>
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-white">
              Legal
            </h3>

            <div className="mt-4 space-y-3 text-sm text-gray-500">
              <Link className="block hover:text-white" href="#">
                Terms
              </Link>
              <Link className="block hover:text-white" href="#">
                Privacy
              </Link>
              <Link className="block hover:text-white" href="#">
                Risk Disclosure
              </Link>
            </div>
          </div>

        </div>

        <div className="mt-12 border-t border-white/10 pt-6 text-sm text-gray-600">
          © 2026 BitNova. All rights reserved.
        </div>

      </div>
    </footer>
  );
}