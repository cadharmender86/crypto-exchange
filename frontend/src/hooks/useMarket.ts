"use client";

import { useEffect, useState } from "react";
import {
  getMarketAssets,
  getMarketTicker,
  getMarketWebSocketUrl,
  MarketAsset,
  MarketTicker,
} from "@/services/market.service";

export function useMarket() {
  const [ticker, setTicker] = useState<MarketTicker[]>([]);
  const [assets, setAssets] = useState<MarketAsset[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined;

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
        console.error("Unable to load market data:", error);
      } finally {
        if (mounted) setLoading(false);
      }
    }

    function connectWebSocket() {
      if (!mounted) return;

      try {
        socket = new WebSocket(getMarketWebSocketUrl());

        socket.onopen = () => {
          console.info("Connected to BitNova live market feed");
        };

        socket.onmessage = (event) => {
          try {
            const update = JSON.parse(event.data) as MarketTicker;
            if (!update.symbol) return;

            setTicker((current) => {
              const index = current.findIndex((item) => item.symbol === update.symbol);
              if (index === -1) return [...current, update];

              const next = [...current];
              next[index] = update;
              return next;
            });
          } catch (error) {
            console.error("Invalid market WebSocket message:", error);
          }
        };

        socket.onclose = () => {
          if (mounted) {
            reconnectTimer = setTimeout(connectWebSocket, 3000);
          }
        };

        socket.onerror = () => {
          socket?.close();
        };
      } catch (error) {
        console.error("Unable to connect to live market feed:", error);
        reconnectTimer = setTimeout(connectWebSocket, 3000);
      }
    }

    loadMarket();
    // Defer the initial socket creation by one event-loop turn. In React
    // development Strict Mode, effects are setup/cleaned up once before the
    // real setup; deferring prevents that temporary socket from being opened
    // and immediately closed before the handshake completes.
    reconnectTimer = setTimeout(connectWebSocket, 0);

    return () => {
      mounted = false;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, []);

  return { ticker, assets, loading };
}
