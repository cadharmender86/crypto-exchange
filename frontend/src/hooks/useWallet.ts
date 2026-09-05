"use client";

import { useCallback, useEffect, useState } from "react";
import { AccountBalance, getAccountBalances } from "@/services/wallet.service";

export function useWallet() {
  const [accounts, setAccounts] = useState<AccountBalance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadWallet = useCallback(async () => {
    try {
      const accountData = await getAccountBalances();
      setAccounts(Array.isArray(accountData) ? accountData : []);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load wallet");
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {

    // Inital wallet load
    void loadWallet();

    const handleOrderCreated = async () => {
      console.log("Wallet refresh event received");
      await loadWallet();
    };

    window.addEventListener("order-created", handleOrderCreated);

    return () => {
      window.removeEventListener("order-created", handleOrderCreated);
    };
  }, [loadWallet]);

  return {
    wallet: null,
    accounts,
    assets: accounts,
    loading,
    error,
    refreshWallet: loadWallet,
  };
}
