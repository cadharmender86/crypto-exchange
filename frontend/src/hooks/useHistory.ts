"use client";

import { useEffect, useState } from 'react';
import { getTradeHistory, getTransactionHistory } from '@/services/history.service';

export function useTradeHistory() {
  const [trades, setTrades] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    setLoading(true);
    try {
      const data = await getTradeHistory();
      setTrades(data);
    } catch {
      setTrades([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  return { trades, loading, refresh };
}

export function useTransactionHistory() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    setLoading(true);
    try {
      const data = await getTransactionHistory();
      setTransactions(data);
    } catch {
      setTransactions([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  return { transactions, loading, refresh };
}