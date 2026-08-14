"use client";

import { useEffect, useState } from "react";
import { getWalletBalance } from "@/services/wallet.service";

export function useWallet() {
  const [wallet, setWallet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadWallet() {
      try {
        const data = await getWalletBalance();
        setWallet(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadWallet();
  }, []);

  return { wallet, loading, error };
}
