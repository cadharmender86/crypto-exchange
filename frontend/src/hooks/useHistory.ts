"use client";

import { useEffect, useState } from 'react';
import { getTradeHistory, getTransactionHistory } from '@/services/history.service';

export function useTradeHistory() {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTradeHistory()
      .then(setTrades)
      .catch(() => setTrades([]))
      .finally(() => setLoading(false));
  }, []);

  return { trades, loading };
}

export function useTransactionHistory() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTransactionHistory()
      .then(setTransactions)
      .catch(() => setTransactions([]))
      .finally(() => setLoading(false));
  }, []);

  return { transactions, loading };
}
