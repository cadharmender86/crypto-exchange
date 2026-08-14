"use client";

import { useEffect, useState } from "react";
import { getMarketAssets, getMarketTicker } from "@/services/market.service";

export function useMarket() {
  const [ticker, setTicker] = useState<any[]>([]);
  const [assets, setAssets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMarket() {
      try {
        const [tickerData, assetData] = await Promise.all([
          getMarketTicker(),
          getMarketAssets(),
        ]);

        setTicker(tickerData || []);
        setAssets(assetData || []);
      } finally {
        setLoading(false);
      }
    }

    loadMarket();
  }, []);

  return { ticker, assets, loading };
}
