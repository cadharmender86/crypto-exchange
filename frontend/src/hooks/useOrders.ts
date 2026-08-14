"use client";

import { useEffect, useState } from "react";
import { getOpenOrders } from "@/services/order.service";

export function useOrders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadOrders() {
      try {
        const data = await getOpenOrders();
        setOrders(data);
      } finally {
        setLoading(false);
      }
    }

    loadOrders();
  }, []);

  return { orders, loading };
}
