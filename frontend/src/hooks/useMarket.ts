"use client";

import { useEffect, useState } from "react";
import { getMarketTicker } from "@/services/market.service";

export function useMarket() {
  const [ticker, setTicker] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTicker() {
      try {
        const data = await getMarketTicker();
        setTicker(data);
      } finally {
        setLoading(false);
      }
    }

    loadTicker();
  }, []);

  return { ticker, loading };
}
