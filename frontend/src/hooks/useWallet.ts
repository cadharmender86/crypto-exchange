"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AccountBalance,
  getAccountBalances,
} from "@/services/wallet.service";

export function useWallet() {
  const [accounts, setAccounts] = useState<AccountBalance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadWallet = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const accountData = await getAccountBalances();
      setAccounts(Array.isArray(accountData) ? accountData : []);
    } catch (err: any) {
      setError(err?.message || "Failed to load wallet");
      setAccounts([]);
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
    wallet: null,
    accounts,
    assets: accounts,
    loading,
    error,
    refreshWallet: loadWallet,
  };
}
