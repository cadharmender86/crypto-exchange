"use client";

export default function BuySellPanel() {
  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-5 text-white">
      <div className="mb-4 flex gap-2">
        <button className="flex-1 rounded bg-green-600 py-2">BUY</button>
        <button className="flex-1 rounded bg-red-600 py-2">SELL</button>
      </div>
      <input className="mb-3 w-full rounded bg-gray-900 p-3" placeholder="Price" />
      <input className="mb-3 w-full rounded bg-gray-900 p-3" placeholder="Quantity" />
      <button className="w-full rounded bg-blue-600 py-3">Place Order</button>
    </section>
  );
}
