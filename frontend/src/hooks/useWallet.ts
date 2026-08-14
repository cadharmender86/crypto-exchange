"use client";

import { useCallback, useEffect, useState } from "react";
import { getWalletBalance } from "@/services/wallet.service";

export function useWallet() {
  const [wallet, setWallet] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  const loadWallet = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getWalletBalance();
      setWallet(data);
    } catch (err: any) {
      setError(err.message);
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

  return { wallet, loading, error, refreshWallet: loadWallet };
}
