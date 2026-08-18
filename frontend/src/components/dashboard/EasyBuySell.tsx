"use client";

import { useMemo, useState } from "react";
import CoinSelectorModal from "./CoinSelectorModal";
import OrderConfirmationModal from "./OrderConfirmationModal";
import CoinIcon from "../common/CoinIcon";
import { useMarket } from "@/hooks/useMarket";
import { useWallet } from "@/hooks/useWallet";
import { createOrder } from "@/services/order.service";

const defaultCoins = ["USDT", "BTC", "ETH", "SOL"];
const TRADING_FEE_PERCENT = 0.1;

export default function EasyBuySell() {
  const { assets = [], ticker = [] } = useMarket();
  const { wallet } = useWallet();
  const coins = assets.length ? assets.slice(0, 6).map((c: any) => c.symbol) : defaultCoins;
  const [selectedCoin, setSelectedCoin] = useState("USDT");
  const [mode, setMode] = useState<"BUY" | "SELL">("BUY");
  const [amount, setAmount] = useState("");
  const [showCoinModal, setShowCoinModal] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");
  const selectedTicker: any = useMemo(() => ticker.find((item: any) => item.symbol === `${selectedCoin}INR` || item.symbol === `${selectedCoin}/INR`), [ticker, selectedCoin]);
  const price = Number(selectedTicker?.last_price || selectedTicker?.price || selectedTicker?.last || 0);
  const payAmount = Number(amount || 0);
  const receiveAmount = price && payAmount ? (payAmount / price).toFixed(8) : "0.00000000";
  const fee = payAmount * TRADING_FEE_PERCENT / 100;
  const totalPayable = payAmount + fee;
  const availableINR = wallet?.available ?? 0;
  const insufficientBalance = mode === "BUY" && totalPayable > availableINR;

  async function handleConfirmOrder() {
    setSubmitting(true); setMessage("");
    try { const response = await createOrder({ symbol: `${selectedCoin}/INR`, side: mode, amount: payAmount, quote_currency: "INR" }); window.dispatchEvent(new CustomEvent("order-created", { detail: response })); setShowConfirm(false); setAmount(""); setMessage("Order placed successfully"); }
    catch { setMessage("Order placement failed"); }
    finally { setSubmitting(false); }
  }

  return (
    <section className="h-full rounded-lg border border-white/[0.06] bg-[#10161d] p-4 text-white">
      <div className="mb-3 flex items-center justify-between"><h2 className="text-sm font-bold">Easy Buy / Sell</h2></div>
      <div className="mb-2 flex items-center gap-2 overflow-hidden">
        {coins.slice(0, 4).map((coin) => <button key={coin} onClick={() => setSelectedCoin(coin)} className={`flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-[10px] font-bold ${selectedCoin === coin ? "bg-white text-slate-900" : "bg-[#18202a] text-slate-300"}`}><CoinIcon symbol={coin} size={18}/>{coin}</button>)}
        <button onClick={() => setShowCoinModal(true)} className="shrink-0 rounded-md border border-blue-500/30 bg-blue-500/10 px-2 py-1.5 text-[9px] font-semibold text-blue-400">More Coins</button>
      </div>
      <div className="grid grid-cols-2 rounded-md bg-[#17263a] p-0.5 text-[10px] font-bold"><button onClick={() => setMode("BUY")} className={`rounded py-1.5 ${mode === "BUY" ? "bg-emerald-500 text-white" : "text-slate-300"}`}>BUY</button><button onClick={() => setMode("SELL")} className={`rounded py-1.5 ${mode === "SELL" ? "bg-red-500 text-white" : "text-slate-300"}`}>SELL</button></div>
      <div className="mt-2"><label className="text-[9px] text-slate-400">You Pay (INR)</label><div className="mt-1 flex items-center rounded-md border border-white/10 bg-[#0b1219] px-2"><input value={amount} onChange={(e) => setAmount(e.target.value)} className="h-8 min-w-0 flex-1 bg-transparent text-xs outline-none" placeholder="Enter amount"/><span className="text-[9px] font-bold">₹ INR</span></div></div>
      <div className="mt-2"><label className="text-[9px] text-slate-400">You Receive ({selectedCoin})</label><div className="mt-1 flex h-8 items-center justify-between rounded-md border border-white/10 bg-[#0b1219] px-2 text-xs text-slate-400"><span>{receiveAmount}</span><span className="text-[9px] font-bold text-emerald-400">{selectedCoin}</span></div></div>
      {insufficientBalance && <p className="mt-1 text-[9px] text-red-400">Insufficient INR Balance</p>}
      <button disabled={!amount || insufficientBalance || submitting} onClick={() => setShowConfirm(true)} className="mt-3 w-full rounded-md bg-gradient-to-r from-blue-600 to-blue-500 py-2 text-[10px] font-bold disabled:opacity-40">{submitting ? "Submitting..." : `Continue ${mode} ${selectedCoin}`}</button>
      {message && <p className="mt-1 text-center text-[9px] text-emerald-400">{message}</p>}
      <CoinSelectorModal open={showCoinModal} onClose={() => setShowCoinModal(false)} onSelect={setSelectedCoin}/>
      <OrderConfirmationModal open={showConfirm} coin={selectedCoin} mode={mode} payAmount={payAmount} receiveAmount={receiveAmount} fee={fee} onCancel={() => setShowConfirm(false)} onConfirm={handleConfirmOrder}/>
    </section>
  );
}
