"use client";

export default function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-800 bg-[#0b0e11] px-6 text-white">
      <div className="text-xl font-bold text-blue-400">BitNova</div>

      <div className="flex items-center gap-4">
        <button className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium">
          Deposit
        </button>
        <div className="rounded-full bg-gray-800 px-3 py-2 text-sm">DK</div>
      </div>
    </header>
  );
}
