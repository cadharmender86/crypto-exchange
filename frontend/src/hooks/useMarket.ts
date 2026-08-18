"use client";

import { useEffect, useState } from "react";
import { getMarketAssets, getMarketTicker } from "@/services/market.service";

export function useMarket() {
  const [ticker, setTicker] = useState<any[]>([]);
  const [assets, setAssets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function loadMarket() {
      try {
        const [tickerData, assetData] = await Promise.all([
          getMarketTicker(),
          getMarketAssets(),
        ]);

        if (!mounted) return;
        setTicker(tickerData || []);
        setAssets(assetData || []);
      } catch (error) {
        console.error("Unable to load market assets:", error);
        if (mounted) {
          setTicker([]);
          setAssets([]);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadMarket();

    return () => {
      mounted = false;
    };
  }, []);

  return { ticker, assets, loading };
}