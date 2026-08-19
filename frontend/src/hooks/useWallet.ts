"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AccountBalance,
  getAccountBalances,
  getWalletBalance,
  WalletBalance,
} from "@/services/wallet.service";

export function useWallet() {
  const [wallet, setWallet] = useState<WalletBalance | null>(null);
  const [accounts, setAccounts] = useState<AccountBalance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadWallet = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [walletData, accountData] = await Promise.all([
        getWalletBalance(),
        getAccountBalances(),
      ]);

      setWallet(walletData);
      setAccounts(Array.isArray(accountData) ? accountData : []);
    } catch (err: any) {
      setError(err?.message || "Failed to load wallet");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadWallet();

    const refreshWallet = () => loadWallet();

    window.addEventListener("order-created", refreshWallet);

    return () => {
      window.removeEventListener("order-created", refreshWallet);
    };
  }, [loadWallet]);

  return {
    wallet,
    accounts,
    assets: accounts,
    loading,
    error,
    refreshWallet: loadWallet,
  };
}