"use client";

import { useCallback, useEffect, useState } from "react";
import { getTradeHistory, getTransactionHistory } from "@/services/history.service";

type TradeHistoryItem = Awaited<ReturnType<typeof getTradeHistory>>[number];
type TransactionHistoryItem = Awaited<ReturnType<typeof getTransactionHistory>>[number];

export function useTradeHistory() {
  const [trades, setTrades] = useState<TradeHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const data = await getTradeHistory();
      setTrades(data);
    } catch {
      setTrades([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    getTradeHistory()
      .then((data) => { if (active) setTrades(data); })
      .catch(() => { if (active) setTrades([]); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  return { trades, loading, refresh };
}

export function useTransactionHistory() {
  const [transactions, setTransactions] = useState<TransactionHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const data = await getTransactionHistory();
      setTransactions(data);
    } catch {
      setTransactions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    getTransactionHistory()
      .then((data) => { if (active) setTransactions(data); })
      .catch(() => { if (active) setTransactions([]); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  return { transactions, loading, refresh };
}
