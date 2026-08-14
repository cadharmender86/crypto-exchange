import { useEffect, useState } from 'react';
import { orderBookService } from '@/services/orderbook.service';

export function useOrderBook(symbol: string) {
  const [orderBook, setOrderBook] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await orderBookService.getOrderBook(symbol);
        setOrderBook(data);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [symbol]);

  return { orderBook, loading };
}
