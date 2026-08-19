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
    let active = true;

    getAccountBalances()
      .then((accountData) => {
        if (!active) return;
        setAccounts(Array.isArray(accountData) ? accountData : []);
        setError(null);
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load wallet");
        setAccounts([]);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    const refreshWallet = () => { void loadWallet(); };
    window.addEventListener("order-created", refreshWallet);

    return () => {
      active = false;
      window.removeEventListener("order-created", refreshWallet);
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
