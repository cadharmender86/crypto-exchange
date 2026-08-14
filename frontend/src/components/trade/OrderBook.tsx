"use client";

const asks = [
  { price: "95,10,000", qty: "0.02" },
  { price: "95,05,000", qty: "0.05" },
];

const bids = [
  { price: "95,00,000", qty: "0.01" },
  { price: "94,95,000", qty: "0.03" },
];

export default function OrderBook() {
  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318] p-5 text-white">
      <h2 className="mb-4 font-semibold">Order Book</h2>
      <div className="space-y-2 text-sm">
        {asks.map((item) => <div key={item.price} className="flex justify-between text-red-400"><span>{item.price}</span><span>{item.qty}</span></div>)}
        <div className="border-y border-gray-800 py-2 text-center text-green-400">95,00,000</div>
        {bids.map((item) => <div key={item.price} className="flex justify-between text-green-400"><span>{item.price}</span><span>{item.qty}</span></div>)}
      </div>
    </section>
  );
}
