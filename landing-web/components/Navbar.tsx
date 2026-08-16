"use client";

import Link from "next/link";
import { useState } from "react";

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-[#070b14]/90 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 lg:px-8">

        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500 font-bold text-white">
            B
          </div>

          <span className="text-xl font-bold tracking-tight text-white">
            Bit<span className="text-blue-400">Nova</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-7 md:flex">
          <Link href="/markets" className="text-sm text-gray-300 hover:text-white">
            Markets
          </Link>

          <Link href="/buy-sell" className="text-sm text-gray-300 hover:text-white">
            Buy Crypto
          </Link>

          <Link href="/otc" className="text-sm text-gray-300 hover:text-white">
            OTC
          </Link>

          <Link href="/fees" className="text-sm text-gray-300 hover:text-white">
            Fees
          </Link>

          <Link href="#" className="text-sm text-gray-300 hover:text-white">
            Learn
          </Link>
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <Link
            href="/login"
            className="rounded-lg px-4 py-2 text-sm font-medium text-gray-200 hover:bg-white/5"
          >
            Login
          </Link>

          <Link
            href="/register"
            className="rounded-lg bg-blue-500 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-600"
          >
            Get Started
          </Link>
        </div>

        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="text-white md:hidden"
        >
          ☰
        </button>
      </div>

      {menuOpen && (
        <div className="border-t border-white/10 bg-[#070b14] px-4 py-5 md:hidden">
          <div className="flex flex-col gap-4">
            <Link href="/markets">Markets</Link>
            <Link href="/buy-sell">Buy Crypto</Link>
            <Link href="/otc">OTC</Link>
            <Link href="/fees">Fees</Link>
            <Link href="/login">Login</Link>
            <Link href="/register">Get Started</Link>
          </div>
        </div>
      )}
    </header>
  );
}