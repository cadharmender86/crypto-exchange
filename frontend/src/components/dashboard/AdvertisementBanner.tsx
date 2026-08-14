export default function AdvertisementBanner() {
  return (
    <div className="flex min-h-28 w-full items-center justify-between rounded-2xl bg-gradient-to-r from-purple-900 via-blue-900 to-indigo-900 p-6 text-white">
      <div>
        <p className="text-sm uppercase text-blue-200">Refer & Earn</p>
        <h2 className="text-2xl font-bold">Earn up to ₹1000 in BTC</h2>
        <button className="mt-3 rounded-lg bg-blue-600 px-5 py-2 text-sm">Refer Now</button>
      </div>
      <div className="hidden text-right md:block">
        <h3 className="text-xl font-bold">BitNova App</h3>
        <p>Trade on the go. Anytime, Anywhere</p>
      </div>
    </div>
  );
}
