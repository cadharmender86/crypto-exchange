import { useEffect, useState } from 'react';
import { tradeService } from '@/services/trade.service';

export function useRecentTrades(symbol: string) {
  const [trades, setTrades] = useState([]);

  useEffect(() => {
    async function load() {
      const data = await tradeService.getRecentTrades(symbol);
      setTrades(data || []);
    }
    load();
  }, [symbol]);

  return { trades };
}
