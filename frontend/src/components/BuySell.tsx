"use client";

import CoinIcon from "@/components/common/CoinIcon";
import { useMarket } from "@/hooks/useMarket";
import { useWallet } from "@/hooks/useWallet";
import { createOrder, getOpenOrders } from "@/services/order.service";
import { useEffect, useMemo, useState } from "react";

const DEFAULT_COINS = ["BTC", "ETH", "SOL", "USDT"];
const FEE_PERCENT = 0.1;

const candles = [
  [40, 56], [52, 72], [68, 48], [44, 64], [60, 82], [76, 58],
  [55, 74], [70, 88], [84, 66], [62, 78], [73, 92], [86, 70],
  [68, 84], [80, 96], [91, 76], [75, 89], [84, 98], [94, 82],
];

const asks = [
  { price: 5739000, amount: 0.0032 },
  { price: 5737800, amount: 0.0061 },
  { price: 5736500, amount: 0.0048 },
  { price: 5735400, amount: 0.0087 },
  { price: 5734200, amount: 0.0029 },
];

const bids = [
  { price: 5733100, amount: 0.0064 },
  { price: 5732000, amount: 0.0041 },
  { price: 5730800, amount: 0.0092 },
  { price: 5729400, amount: 0.0058 },
  { price: 5728100, amount: 0.0073 },
];

function money(value: number) {
  return value.toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

function compact(value: number) {
  return value.toLocaleString("en-IN", { maximumFractionDigits: 6 });
}

export default function BuySell() {
  const { assets = [], ticker = [] } = useMarket();
  const { accounts = [] } = useWallet();
  const [selectedCoin, setSelectedCoin] = useState("BTC");
  const [side, setSide] = useState<"BUY" | "SELL">("BUY");
  // Backend currently supports LIMIT orders only. Market remains visible but disabled.
  const [orderType] = useState<"LIMIT">("LIMIT");
  const [priceInput, setPriceInput] = useState("");
  const [amountInput, setAmountInput] = useState("");
  const [tab, setTab] = useState("Open Orders");
  const [orders, setOrders] = useState<any[]>([]);
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const coins = assets.length
    ? assets
        .filter((asset) => asset.symbol !== "INR" && asset.trading_enabled)
        .map((asset) => asset.symbol)
    : DEFAULT_COINS;

  const selectedAsset = assets.find((asset) => asset.symbol === selectedCoin);
  const inrAsset = assets.find((asset) => asset.symbol === "INR");
  const selectedAccount = accounts.find((account) => account.asset_id === selectedAsset?.id);
  const inrAccount = accounts.find((account) => account.asset_id === inrAsset?.id);

  const tickerData = useMemo(
    () => ticker.find((item) => item.symbol === `${selectedCoin}INR`),
    [ticker, selectedCoin],
  );

  const livePrice = Number(
    tickerData?.price_inr ?? tickerData?.last_price ?? tickerData?.price ?? 0,
  );

  // LIMIT price is user-controlled. The live market price is only the initial suggestion.
  const price = Number(priceInput || 0);
  const amount = Number(amountInput || 0);
  const total = price > 0 && amount > 0 ? price * amount : 0;
  const fee = total * FEE_PERCENT / 100;
  const buyCost = total + fee;
  const sellReceive = Math.max(0, total - fee);
  const available = side === "BUY"
    ? Number(inrAccount?.available_balance ?? 0)
    : Number(selectedAccount?.available_balance ?? 0);

  const canSubmit = Boolean(
    selectedAsset &&
      inrAsset &&
      price > 0 &&
      amount > 0 &&
      (side === "BUY" ? buyCost <= available : amount <= available),
  );

  useEffect(() => {
    if (livePrice > 0) {
      setPriceInput(livePrice.toFixed(2));
    } else {
      setPriceInput("");
    }
    setAmountInput("");
    setMessage("");
  }, [selectedCoin, livePrice]);

  async function loadOrders() {
    try {
      const data = await getOpenOrders();
      setOrders(Array.isArray(data) ? data : []);
    } catch {
      setOrders([]);
    }
  }

  useEffect(() => {
    loadOrders();
    const refresh = () => loadOrders();
    window.addEventListener("order-created", refresh);
    return () => window.removeEventListener("order-created", refresh);
  }, []);

  function selectCoin(coin: string) {
    setSelectedCoin(coin);
  }

  function setMax(currentSide: "BUY" | "SELL") {
    if (currentSide === "BUY") {
      // Leave enough INR for the 0.1% fee.
      const maxQuantity = available > 0 && price > 0
        ? available / (price * (1 + FEE_PERCENT / 100))
        : 0;
      setAmountInput(maxQuantity.toFixed(8));
    } else {
      setAmountInput(available.toFixed(8));
    }
  }

  async function submitOrder(currentSide: "BUY" | "SELL") {
    if (!canSubmit || !selectedAsset || !inrAsset) return;

    setSide(currentSide);
    setSubmitting(true);
    setMessage("");

    try {
      await createOrder({
        base_asset_id: selectedAsset.id,
        quote_asset_id: inrAsset.id,
        side: currentSide,
        order_type: orderType,
        price,
        quantity: amount,
      });
      setAmountInput("");
      setMessage(`${currentSide} order placed successfully`);
      window.dispatchEvent(new Event("order-created"));
    } catch (error: any) {
      setMessage(error?.message || "Order placement failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto max-w-[1400px] px-3 py-4 md:px-5">
      <div className="mb-3 flex flex-wrap items-center gap-2 rounded-xl border border-white/[0.06] bg-[#10161d] p-2">
        {coins.map((coin) => (
          <button
            key={coin}
            onClick={() => selectCoin(coin)}
            className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-bold ${
              selectedCoin === coin
                ? "bg-white text-slate-900"
                : "text-slate-400 hover:bg-white/5 hover:text-white"
            }`}
          >
            <CoinIcon symbol={coin} size={24} /> {coin}/INR
          </button>
        ))}
      </div>

      <section className="rounded-xl border border-white/[0.06] bg-[#10161d]">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/[0.06] px-4 py-4">
          <div className="flex items-center gap-3">
            <CoinIcon symbol={selectedCoin} size={40} />
            <div>
              <h1 className="text-xl font-bold">{selectedCoin}/INR</h1>
              <p className="text-sm text-slate-500">Spot Market</p>
            </div>
            <div className="ml-3">
              <p className="text-2xl font-bold">₹ {money(livePrice)}</p>
              <p className="text-sm text-emerald-400">
                +{Number(tickerData?.change_24h ?? 0).toFixed(2)}% 24h
              </p>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-5 text-right text-sm">
            <div>
              <p className="text-slate-500">24h High</p>
              <p className="mt-1 font-semibold">₹ {money(Number(tickerData?.high_24h ?? 0))}</p>
            </div>
            <div>
              <p className="text-slate-500">24h Low</p>
              <p className="mt-1 font-semibold">₹ {money(Number(tickerData?.low_24h ?? 0))}</p>
            </div>
            <div>
              <p className="text-slate-500">24h Volume</p>
              <p className="mt-1 font-semibold">
                {compact(Number(tickerData?.volume_24h ?? 0))} {selectedCoin}
              </p>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-[minmax(0,1fr)_330px]">
          <div className="min-h-[440px] border-b border-white/[0.06] p-4 lg:border-b-0 lg:border-r">
            <div className="mb-3 flex items-center justify-between text-sm text-slate-400">
              <span>Price Chart</span>
              <span>1m · 5m · 15m · 1H · 4H · 1D</span>
            </div>
            <div className="relative h-[390px] overflow-hidden rounded-lg border border-white/[0.05] bg-[#0b1118] p-5">
              <div
                className="absolute inset-0 opacity-30"
                style={{
                  backgroundImage:
                    "linear-gradient(rgba(255,255,255,.06) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.06) 1px, transparent 1px)",
                  backgroundSize: "60px 50px",
                }}
              />
              <div className="relative flex h-full items-end justify-between gap-2">
                {candles.map(([low, high], index) => {
                  const bullish = index % 3 !== 0;
                  const bodyHeight = Math.max(14, Math.abs(high - low));
                  return (
                    <div key={index} className="relative h-full w-3 flex-1">
                      <div className="absolute left-1/2 top-[20%] h-[65%] w-px -translate-x-1/2 bg-slate-500" />
                      <div
                        className={`absolute left-1/2 w-2 -translate-x-1/2 rounded-sm ${
                          bullish ? "bg-emerald-400" : "bg-red-400"
                        }`}
                        style={{
                          top: `${100 - high}%`,
                          height: `${bodyHeight / 1.8}%`,
                        }}
                      />
                      <div className="absolute left-0 right-0 top-1/2 h-px bg-blue-400/50" />
                    </div>
                  );
                })}
              </div>
              <div className="absolute right-3 top-[42%] rounded bg-blue-500 px-2 py-1 text-xs font-bold text-white">
                ₹ {money(livePrice)}
              </div>
            </div>
          </div>

          <aside className="p-4">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-base font-bold">Order Book</h2>
              <span className="text-xs text-slate-500">{selectedCoin}/INR</span>
            </div>
            <div className="grid grid-cols-3 text-xs text-slate-500">
              <span>Price (INR)</span>
              <span className="text-right">Amount</span>
              <span className="text-right">Total</span>
            </div>
            <div className="mt-2 space-y-1">
              {asks.map((row) => (
                <div key={row.price} className="grid grid-cols-3 text-xs">
                  <span className="text-red-400">{money(row.price)}</span>
                  <span className="text-right text-slate-300">{row.amount}</span>
                  <span className="text-right text-slate-500">
                    {(row.price * row.amount).toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                  </span>
                </div>
              ))}
            </div>
            <div className="my-4 border-y border-white/[0.06] py-3 text-center text-base font-bold text-blue-400">
              ₹ {money(livePrice)}
            </div>
            <div className="space-y-1">
              {bids.map((row) => (
                <div key={row.price} className="grid grid-cols-3 text-xs">
                  <span className="text-emerald-400">{money(row.price)}</span>
                  <span className="text-right text-slate-300">{row.amount}</span>
                  <span className="text-right text-slate-500">
                    {(row.price * row.amount).toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                  </span>
                </div>
              ))}
            </div>
          </aside>
        </div>

        <div className="border-t border-white/[0.06] p-4">
          <div className="grid gap-5 md:grid-cols-2">
            {(["BUY", "SELL"] as const).map((currentSide) => {
              const active = side === currentSide;
              const currentAvailable = currentSide === "BUY"
                ? Number(inrAccount?.available_balance ?? 0)
                : Number(selectedAccount?.available_balance ?? 0);
              const currentTotal = price > 0 && amount > 0 ? price * amount : 0;
              const currentFee = currentTotal * FEE_PERCENT / 100;
              const currentFinal = currentSide === "BUY"
                ? currentTotal + currentFee
                : Math.max(0, currentTotal - currentFee);

              return (
                <div
                  key={currentSide}
                  className="rounded-xl border border-white/[0.06] bg-[#0b1118] p-4"
                >
                  <div className="mb-4 flex items-center justify-between">
                    <button
                      onClick={() => setSide(currentSide)}
                      className={`text-base font-bold ${
                        active
                          ? currentSide === "BUY"
                            ? "text-emerald-400"
                            : "text-red-400"
                          : "text-slate-500"
                      }`}
                    >
                      {currentSide}
                    </button>
                    <span className="text-xs text-slate-500">
                      Available {currentSide === "BUY" ? "INR" : selectedCoin}: {currentAvailable.toFixed(8)}
                    </span>
                  </div>

                  <div className="mb-3 grid grid-cols-2 rounded-lg bg-[#17202b] p-1 text-sm font-bold">
                    <button
                      type="button"
                      disabled
                      title="Market orders are not enabled yet"
                      className="cursor-not-allowed rounded py-2 text-slate-600"
                    >
                      Market
                    </button>
                    <button
                      type="button"
                      className="rounded bg-white py-2 text-slate-900"
                    >
                      Limit
                    </button>
                  </div>

                  <label className="mb-2 block text-xs text-slate-500">
                    Limit Price (INR)
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={priceInput}
                      onChange={(e) => setPriceInput(e.target.value)}
                      className="mt-1 h-10 w-full rounded-lg border border-white/10 bg-[#070c12] px-3 text-sm outline-none focus:border-blue-500/50"
                      placeholder="Enter limit price"
                    />
                  </label>

                  <label className="mb-2 block text-xs text-slate-500">
                    Quantity ({selectedCoin})
                    <div className="mt-1 flex rounded-lg border border-white/10 bg-[#070c12]">
                      <input
                        type="number"
                        min="0"
                        step="any"
                        value={amountInput}
                        onChange={(e) => setAmountInput(e.target.value)}
                        className="h-10 min-w-0 flex-1 bg-transparent px-3 text-sm outline-none"
                        placeholder={`Enter ${selectedCoin} quantity`}
                      />
                      <button
                        type="button"
                        onClick={() => setMax(currentSide)}
                        className="px-3 text-xs font-bold text-blue-400"
                      >
                        MAX
                      </button>
                    </div>
                  </label>

                  <div className="mb-2 block text-xs text-slate-500">
                    Total (INR)
                    <div className="mt-1 flex h-10 items-center rounded-lg border border-white/10 bg-[#070c12] px-3 text-sm font-semibold text-white">
                      ₹ {money(currentTotal)}
                    </div>
                  </div>

                  <div className="mb-2 flex justify-between text-xs text-slate-500">
                    <span>Fee ({FEE_PERCENT}%)</span>
                    <span>₹ {money(currentFee)}</span>
                  </div>

                  <div className="mb-3 flex justify-between text-xs text-slate-400">
                    <span>{currentSide === "BUY" ? "You Pay" : "You Receive"}</span>
                    <span className="font-semibold text-white">₹ {money(currentFinal)}</span>
                  </div>

                  {currentSide === "BUY" && currentTotal > 0 && currentFinal > currentAvailable && (
                    <p className="mb-2 text-xs text-red-400">Insufficient INR balance</p>
                  )}
                  {currentSide === "SELL" && amount > currentAvailable && (
                    <p className="mb-2 text-xs text-red-400">Insufficient {selectedCoin} balance</p>
                  )}

                  <button
                    type="button"
                    onClick={() => submitOrder(currentSide)}
                    disabled={!canSubmit || submitting}
                    className={`w-full rounded-lg py-3 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-40 ${
                      currentSide === "BUY"
                        ? "bg-emerald-500 hover:bg-emerald-400"
                        : "bg-red-500 hover:bg-red-400"
                    }`}
                  >
                    {submitting ? "Placing..." : `${currentSide} ${selectedCoin}`}
                  </button>
                </div>
              );
            })}
          </div>
          {message && (
            <p
              className={`mt-3 text-center text-sm ${
                message.includes("successfully") ? "text-emerald-400" : "text-red-400"
              }`}
            >
              {message}
            </p>
          )}
        </div>

        <div className="border-t border-white/[0.06] px-4 pt-2">
          <div className="flex gap-6 overflow-x-auto text-sm font-semibold">
            {["Open Orders", "Order History", "Trade History"].map((item) => (
              <button
                key={item}
                onClick={() => setTab(item)}
                className={`border-b-2 px-2 py-3 ${
                  tab === item
                    ? "border-blue-400 text-white"
                    : "border-transparent text-slate-500"
                }`}
              >
                {item}
              </button>
            ))}
          </div>
          <div className="min-h-[90px] py-5 text-sm text-slate-400">
            {tab === "Open Orders" &&
              (orders.length
                ? orders.slice(0, 5).map((order) => (
                    <div
                      key={order.id}
                      className="flex justify-between border-b border-white/[0.05] py-2"
                    >
                      <span>{order.symbol || `${selectedCoin}/INR`}</span>
                      <span>{order.side}</span>
                      <span>{order.status}</span>
                      <span>{order.amount || order.quantity}</span>
                    </div>
                  ))
                : "No open orders")}
            {tab === "Order History" &&
              "Order history will appear here after completed or cancelled orders."}
            {tab === "Trade History" &&
              "Trade fills will appear here when orders are matched."}
          </div>
        </div>
      </section>
    </main>
  );
}
