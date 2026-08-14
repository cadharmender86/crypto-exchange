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

  const selectedTicker: any = useMemo(() => ticker.find((item: any) => item.symbol === `${selectedCoin}INR` || item.symbol === `${selectedCoin}/INR`), [ticker, selectedCoin]);
  const price = Number(selectedTicker?.last_price || selectedTicker?.price || selectedTicker?.last || 0);
  const payAmount = Number(amount || 0);
  const receiveAmount = price && payAmount ? (payAmount / price).toFixed(8) : "0.00000000";
  const fee = payAmount * TRADING_FEE_PERCENT / 100;
  const totalPayable = payAmount + fee;
  const availableINR = wallet?.available ?? 0;
  const insufficientBalance = mode === "BUY" && totalPayable > availableINR;

  async function handleConfirmOrder() {
    setSubmitting(true);
    try {
      await createOrder({
        symbol: `${selectedCoin}/INR`,
        side: mode,
        amount: payAmount,
        quote_currency: "INR",
      });
      setShowConfirm(false);
      setAmount("");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="rounded-2xl border border-gray-800 bg-[#111318] p-6">
      <div className="mb-5 flex justify-between"><h2 className="text-lg font-semibold text-white">Easy Buy / Sell</h2><button className="text-blue-400" onClick={() => setShowCoinModal(true)}>More Coins</button></div>
      <div className="mb-5 flex flex-wrap gap-3">{coins.map((coin) => <button key={coin} onClick={() => setSelectedCoin(coin)} className={`flex items-center gap-2 rounded-full px-4 py-2 ${selectedCoin === coin ? "bg-blue-600 text-white" : "bg-[#1b2028] text-gray-300"}`}><CoinIcon symbol={coin} size={22}/>{coin}</button>)}</div>
      <div className="text-sm text-gray-400">Trading Pair: <span className="text-white">{selectedCoin}/INR</span></div>
      <div className="mb-4 text-sm text-gray-400">Market Price: <span className="text-white">₹{price || "--"}</span></div>
      <div className="grid grid-cols-2 rounded-xl bg-[#0b0e11] p-1 mb-4"><button onClick={() => setMode("BUY")} className="py-3">BUY</button><button onClick={() => setMode("SELL")} className="py-3">SELL</button></div>
      <input value={amount} onChange={(e)=>setAmount(e.target.value)} className="w-full rounded-xl bg-[#0b0e11] p-4 text-white" placeholder="Enter amount" />
      <div className="mt-3 text-white">Receive: {receiveAmount} {selectedCoin}</div>
      {insufficientBalance && <p className="mt-3 text-red-400">Insufficient INR Balance</p>}
      <button disabled={!amount || insufficientBalance || submitting} onClick={() => setShowConfirm(true)} className="mt-5 w-full rounded-xl bg-blue-600 py-3 text-white">Review {mode} {selectedCoin}</button>
      <CoinSelectorModal open={showCoinModal} onClose={() => setShowCoinModal(false)} onSelect={setSelectedCoin}/>
      <OrderConfirmationModal open={showConfirm} coin={selectedCoin} mode={mode} payAmount={payAmount} receiveAmount={receiveAmount} fee={fee} onCancel={()=>setShowConfirm(false)} onConfirm={handleConfirmOrder}/>
      {submitting && <p className="mt-2 text-center text-gray-400">Submitting order...</p>}
    </section>
  );
}
