export default function AdvertisementBanner() {
  return (
    <section className="relative min-h-[124px] overflow-hidden rounded-xl border border-purple-500/25 bg-[radial-gradient(circle_at_42%_50%,rgba(139,37,220,.42),transparent_29%),linear-gradient(100deg,#10135d,#24106b_54%,#111054)] px-7 py-4 shadow-[0_15px_50px_rgba(52,18,130,.25)]">
      <div className="pointer-events-none absolute left-[27%] top-[-80px] h-56 w-56 rounded-full bg-fuchsia-500/20 blur-3xl" />
      <div className="pointer-events-none absolute left-[42%] top-1/2 h-24 w-24 -translate-y-1/2 rounded-full border border-yellow-300/20 shadow-[0_0_45px_rgba(250,204,21,.18)]" />
      <div className="pointer-events-none absolute right-[27%] top-0 h-full w-px bg-white/10" />

      <div className="relative flex h-full items-center justify-between gap-6">
        <div className="min-w-0">
          <p className="text-[11px] font-bold uppercase tracking-wide text-white">REFER &amp; EARN</p>
          <h2 className="mt-2 text-lg font-bold md:text-xl">Earn up to <span className="text-2xl">₹1000</span> in BTC</h2>
          <button className="mt-2 rounded-md bg-gradient-to-r from-violet-600 to-fuchsia-500 px-5 py-1.5 text-[11px] font-bold shadow-lg shadow-fuchsia-700/20 transition hover:brightness-110">Refer Now</button>
        </div>

        <div className="hidden h-20 w-28 items-center justify-center md:flex">
          <div className="relative h-16 w-16 rotate-3 rounded-xl border-[4px] border-yellow-400 bg-gradient-to-br from-fuchsia-700 via-purple-700 to-purple-950 shadow-[0_0_35px_rgba(250,204,21,.45)]">
            <div className="absolute left-1/2 top-0 h-full w-2 -translate-x-1/2 bg-yellow-300/80" />
            <div className="absolute left-1/2 top-1/2 h-2 w-full -translate-x-1/2 -translate-y-1/2 bg-yellow-300/80" />
            <div className="absolute -left-1 -top-2 h-4 w-8 rotate-[-28deg] rounded-full border-2 border-yellow-300" />
            <div className="absolute -right-1 -top-2 h-4 w-8 rotate-[28deg] rounded-full border-2 border-yellow-300" />
          </div>
        </div>

        <div className="hidden min-w-[270px] border-l border-white/10 pl-7 md:block">
          <h3 className="text-lg font-bold">BitNova App</h3>
          <p className="mt-1 text-sm text-slate-200">Trade on the go</p>
          <p className="text-sm text-slate-200">Anytime, Anywhere</p>
          <div className="mt-2 flex gap-2"><span className="rounded bg-black/80 px-2 py-1 text-[9px]"> App Store</span><span className="rounded bg-black/80 px-2 py-1 text-[9px]">▶ Google Play</span></div>
        </div>

        <button className="absolute right-2 top-2 flex h-7 w-7 items-center justify-center rounded-full bg-white/10 text-sm text-white hover:bg-white/20" aria-label="Close">×</button>
      </div>
    </section>
  );
}
