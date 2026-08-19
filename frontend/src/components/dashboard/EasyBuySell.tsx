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
  const { accounts = [] } = useWallet();

  const [selectedCoin, setSelectedCoin] = useState("USDT");
  const [mode, setMode] = useState<"BUY" | "SELL">("BUY");
  const [amount, setAmount] = useState("");
  const [showCoinModal, setShowCoinModal] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  const isBuy = mode === "BUY";

  // Only show tradable crypto assets, never INR in the coin selector.
  const coins = assets.length
    ? assets
        .filter(
          (asset) =>
            asset.symbol !== "INR" && asset.trading_enabled,
        )
        .slice(0, 6)
        .map((asset) => asset.symbol)
    : defaultCoins;

  const selectedAsset = assets.find(
    (asset) => asset.symbol === selectedCoin,
  );

  const inrAsset = assets.find(
    (asset) => asset.symbol === "INR",
  );

  /*
   * Find the selected user's account.
   */
  const selectedAccount = accounts.find(
    (account) => account.asset_id === selectedAsset?.id,
  );

  /*
   * INR account.
   */
  const inrAccount = accounts.find(
    (account) => account.asset_id === inrAsset?.id,
  );

  /*
   * Current market price.
   *
   * Currently your market.service.ts returns an empty ticker array,
   * so this will remain 0 until the ticker API is implemented.
   */
  const selectedTicker = useMemo(
    () =>
      ticker.find(
        (item: any) =>
          item.symbol === `${selectedCoin}INR` ||
          item.symbol === `${selectedCoin}/INR`,
      ),
    [ticker, selectedCoin],
  );

  const price = Number(
    selectedTicker?.last_price ||
      selectedTicker?.price ||
      0,
  );

  const payAmount = Number(amount || 0);

  /*
   * BUY:
   * User enters INR.
   * Backend quantity must be crypto quantity.
   *
   * Example:
   * ₹10,000 / ₹90 = 111.11111111 USDT
   *
   * SELL:
   * User enters crypto quantity.
   *
   * Example:
   * 10 USDT = quantity 10
   */
  const quantity = isBuy
    ? price > 0
      ? payAmount / price
      : 0
    : payAmount;

  /*
   * BUY:
   * INR -> selected crypto
   *
   * SELL:
   * selected crypto -> INR
   */
  const receiveAmount =
    price > 0 && payAmount > 0
      ? isBuy
        ? quantity.toFixed(8)
        : (payAmount * price).toFixed(2)
      : isBuy
        ? "0.00000000"
        : "0.00";

  /*
   * Fee is calculated on the amount entered by the user.
   */
  const fee = payAmount * TRADING_FEE_PERCENT / 100;

  /*
   * BUY:
   * User needs INR + fee.
   *
   * SELL:
   * User needs selected crypto.
   *
   * The backend remains the final authority for balance validation.
   */
  const requiredBalance = isBuy
    ? payAmount + fee
    : payAmount;

  const availableBalance = isBuy
    ? Number(inrAccount?.available_balance ?? 0)
    : Number(selectedAccount?.available_balance ?? 0);

  const insufficientBalance =
    payAmount > 0 &&
    requiredBalance > availableBalance;

  const missingAssets =
    !selectedAsset ||
    !inrAsset;

  async function handleConfirmOrder() {
    setSubmitting(true);
    setMessage("");

    try {
      if (!selectedAsset || !inrAsset) {
        throw new Error("Trading assets are unavailable");
      }

      if (price <= 0) {
        throw new Error("Market price is unavailable");
      }

      if (payAmount <= 0) {
        throw new Error("Enter a valid amount");
      }

      if (insufficientBalance) {
        throw new Error(
          `Insufficient ${isBuy ? "INR" : selectedCoin} balance`,
        );
      }

      const response = await createOrder({
        base_asset_id: selectedAsset.id,
        quote_asset_id: inrAsset.id,
        side: mode,
        order_type: "LIMIT",
        price,
        quantity,
      });

      window.dispatchEvent(
        new CustomEvent("order-created", {
          detail: response,
        }),
      );

      setShowConfirm(false);
      setAmount("");
      setMessage("Order placed successfully");
    } catch (error: any) {
      setMessage(
        error?.message || "Order placement failed",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="h-full rounded-lg border border-white/[0.06] bg-[#10161d] p-4 text-white">

      {/* Header */}
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-bold">
          Easy Buy / Sell
        </h2>
      </div>

      {/* Coin selector */}
      <div className="mb-2 flex items-center gap-2 overflow-hidden">
        {coins.slice(0, 4).map((coin) => (
          <button
            key={coin}
            onClick={() => {
              setSelectedCoin(coin);
              setMessage("");
            }}
            className={`flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-[10px] font-bold ${
              selectedCoin === coin
                ? "bg-white text-slate-900"
                : "bg-[#18202a] text-slate-300"
            }`}
          >
            <CoinIcon
              symbol={coin}
              size={18}
            />

            {coin}
          </button>
        ))}

        <button
          onClick={() => setShowCoinModal(true)}
          className="shrink-0 rounded-md border border-blue-500/30 bg-blue-500/10 px-2 py-1.5 text-[9px] font-semibold text-blue-400"
        >
          More Coins
        </button>
      </div>

      {/* BUY / SELL */}
      <div className="grid grid-cols-2 rounded-md bg-[#17263a] p-0.5 text-[10px] font-bold">

        <button
          onClick={() => {
            setMode("BUY");
            setMessage("");
          }}
          className={`rounded py-1.5 transition ${
            isBuy
              ? "bg-emerald-500 text-white"
              : "text-slate-300 hover:text-white"
          }`}
        >
          BUY
        </button>

        <button
          onClick={() => {
            setMode("SELL");
            setMessage("");
          }}
          className={`rounded py-1.5 transition ${
            !isBuy
              ? "bg-red-500 text-white"
              : "text-slate-300 hover:text-white"
          }`}
        >
          SELL
        </button>
      </div>

      {/* You Pay */}
      <div className="mt-2">
        <label className="text-[9px] text-slate-400">
          You Pay ({isBuy ? "INR" : selectedCoin})
        </label>

        <div
          className={`mt-1 flex items-center rounded-md border bg-[#0b1219] px-2 ${
            isBuy
              ? "border-emerald-500/20"
              : "border-red-500/20"
          }`}
        >
          <input
            type="number"
            min="0"
            step="any"
            value={amount}
            onChange={(e) => {
              setAmount(e.target.value);
              setMessage("");
            }}
            className="h-8 min-w-0 flex-1 bg-transparent text-xs outline-none"
            placeholder="Enter amount"
          />

          <span
            className={`text-[9px] font-bold ${
              isBuy
                ? "text-emerald-400"
                : "text-red-400"
            }`}
          >
            {isBuy ? "₹ INR" : selectedCoin}
          </span>
        </div>
      </div>

      {/* You Receive */}
      <div className="mt-2">
        <label className="text-[9px] text-slate-400">
          You Receive ({isBuy ? selectedCoin : "INR"})
        </label>

        <div
          className={`mt-1 flex h-8 items-center justify-between rounded-md border bg-[#0b1219] px-2 text-xs ${
            isBuy
              ? "border-emerald-500/20"
              : "border-red-500/20"
          }`}
        >
          <span className="text-slate-400">
            {receiveAmount}
          </span>

          <span
            className={`text-[9px] font-bold ${
              isBuy
                ? "text-emerald-400"
                : "text-red-400"
            }`}
          >
            {isBuy ? selectedCoin : "INR"}
          </span>
        </div>
      </div>

      {/* Balance */}
      {payAmount > 0 && (
        <p className="mt-1 text-[9px] text-slate-500">
          Available:{" "}
          <span
            className={
              insufficientBalance
                ? "text-red-400"
                : isBuy
                  ? "text-emerald-400"
                  : "text-red-400"
            }
          >
            {availableBalance.toFixed(8)}{" "}
            {isBuy ? "INR" : selectedCoin}
          </span>
        </p>
      )}

      {/* Insufficient balance */}
      {insufficientBalance && (
        <p className="mt-1 text-[9px] text-red-400">
          Insufficient{" "}
          {isBuy ? "INR" : selectedCoin} Balance
        </p>
      )}

      {/* Price unavailable */}
      {price <= 0 && (
        <p className="mt-1 text-[9px] text-yellow-400">
          Price unavailable
        </p>
      )}

      {/* Submit */}
      <button
        disabled={
          !amount ||
          payAmount <= 0 ||
          insufficientBalance ||
          submitting ||
          missingAssets ||
          price <= 0
        }
        onClick={() => setShowConfirm(true)}
        className={`mt-3 w-full rounded-md py-2 text-[10px] font-bold text-white transition disabled:cursor-not-allowed disabled:opacity-40 ${
          isBuy
            ? "bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400"
            : "bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400"
        }`}
      >
        {submitting
          ? "Submitting..."
          : `Continue ${mode} ${selectedCoin}`}
      </button>

      {/* Message */}
      {message && (
        <p
          className={`mt-1 text-center text-[9px] ${
            message === "Order placed successfully"
              ? "text-emerald-400"
              : "text-red-400"
          }`}
        >
          {message}
        </p>
      )}

      {/* Coin selector modal */}
      <CoinSelectorModal
        open={showCoinModal}
        onClose={() => setShowCoinModal(false)}
        onSelect={(coin) => {
          setSelectedCoin(coin);
          setMessage("");
        }}
      />

      {/* Confirmation modal */}
      <OrderConfirmationModal
        open={showConfirm}
        coin={selectedCoin}
        mode={mode}
        payAmount={payAmount}
        receiveAmount={receiveAmount}
        fee={fee}
        onCancel={() => setShowConfirm(false)}
        onConfirm={handleConfirmOrder}
      />
    </section>
  );
}