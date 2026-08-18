"use client";

import { useCallback, useEffect, useState } from "react";
import {
  getWalletBalance,
  getWalletAssets,
} from "@/services/wallet.service";

export function useWallet() {
  const [wallet, setWallet] = useState<any>(null);
  const [assets, setAssets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  const loadWallet = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [walletData, assetsData] = await Promise.all([
        getWalletBalance(),
        getWalletAssets(),
      ]);

      setWallet(walletData);
      setAssets(Array.isArray(assetsData) ? assetsData : []);
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
    assets,
    loading,
    error,
    refreshWallet: loadWallet,
  };
}
