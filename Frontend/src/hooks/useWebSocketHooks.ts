'use client';

import { useEffect, useCallback, useRef } from 'react';
import { useWebSocket } from '@/context/WebSocketContext';

/**
 * Hook for subscribing to real-time product updates
 */
export const useProductUpdates = (onProductUpdate?: (data: any) => void) => {
  const { subscribeToChannel, unsubscribeFromChannel, addEventListener } = useWebSocket();

  useEffect(() => {
    subscribeToChannel('products');
    return () => unsubscribeFromChannel('products');
  }, [subscribeToChannel, unsubscribeFromChannel]);

  useEffect(() => {
    if (!onProductUpdate) return;

    const cleanup = addEventListener('product_updated', onProductUpdate);
    return cleanup;
  }, [addEventListener, onProductUpdate]);
};

/**
 * Hook for subscribing to real-time stock movement updates
 */
export const useStockMovementUpdates = (onStockMovement?: (data: any) => void) => {
  const { subscribeToChannel, unsubscribeFromChannel, addEventListener } = useWebSocket();

  useEffect(() => {
    subscribeToChannel('stock_movements');
    return () => unsubscribeFromChannel('stock_movements');
  }, [subscribeToChannel, unsubscribeFromChannel]);

  useEffect(() => {
    if (!onStockMovement) return;

    const cleanup = addEventListener('stock_movement_created', onStockMovement);
    return cleanup;
  }, [addEventListener, onStockMovement]);
};

/**
 * Hook for subscribing to real-time stock transfer updates
 */
export const useStockTransferUpdates = (onStockTransfer?: (data: any) => void) => {
  const { subscribeToChannel, unsubscribeFromChannel, addEventListener } = useWebSocket();

  useEffect(() => {
    subscribeToChannel('stock_transfers');
    return () => unsubscribeFromChannel('stock_transfers');
  }, [subscribeToChannel, unsubscribeFromChannel]);

  useEffect(() => {
    if (!onStockTransfer) return;

    const cleanup = addEventListener('stock_transfer_updated', onStockTransfer);
    return cleanup;
  }, [addEventListener, onStockTransfer]);
};

/**
 * Hook for subscribing to dashboard updates
 */
export const useDashboardUpdates = (onDashboardUpdate?: (data: any) => void) => {
  const { subscribeToChannel, unsubscribeFromChannel, addEventListener } = useWebSocket();

  useEffect(() => {
    subscribeToChannel('dashboard');
    return () => unsubscribeFromChannel('dashboard');
  }, [subscribeToChannel, unsubscribeFromChannel]);

  useEffect(() => {
    if (!onDashboardUpdate) return;

    const cleanupUpdate = addEventListener('dashboard_update', onDashboardUpdate);
    const cleanupStats = addEventListener('dashboard_stats_update', onDashboardUpdate);
    
    return () => {
      cleanupUpdate();
      cleanupStats();
    };
  }, [addEventListener, onDashboardUpdate]);
};

/**
 * Hook for handling low stock alerts
 */
export const useLowStockAlerts = (onLowStockAlert?: (data: any) => void) => {
  const { addEventListener } = useWebSocket();

  useEffect(() => {
    if (!onLowStockAlert) return;

    const cleanup = addEventListener('low_stock_alert', onLowStockAlert);
    return cleanup;
  }, [addEventListener, onLowStockAlert]);
};

/**
 * Hook for real-time data with automatic refresh
 */
export const useRealTimeData = <T>(
  fetchFunction: () => Promise<T>,
  dependencies: any[] = [],
  options?: {
    intervalMs?: number;
    enableWebSocket?: boolean;
    webSocketEvents?: string[];
  }
) => {
  const { addEventListener } = useWebSocket();
  const { intervalMs = 30000, enableWebSocket = true, webSocketEvents = [] } = options || {};
  
  const dataRef = useRef<T | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const newData = await fetchFunction();
      dataRef.current = newData;
      return newData;
    } catch (error) {
      console.error('Error fetching real-time data:', error);
      throw error;
    }
  }, [fetchFunction]);

  // Set up periodic refresh
  useEffect(() => {
    const setupInterval = () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      
      intervalRef.current = setInterval(fetchData, intervalMs);
    };

    setupInterval();

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchData, intervalMs]);

  // Set up WebSocket listeners for immediate updates
  useEffect(() => {
    if (!enableWebSocket || webSocketEvents.length === 0) return;

    const cleanups: (() => void)[] = [];

    webSocketEvents.forEach(eventType => {
      const cleanup = addEventListener(eventType, () => {
        // Refresh data when WebSocket event is received
        fetchData();
      });
      cleanups.push(cleanup);
    });

    return () => {
      cleanups.forEach(cleanup => cleanup());
    };
  }, [addEventListener, enableWebSocket, webSocketEvents, fetchData]);

  return {
    refreshData: fetchData,
    getCurrentData: () => dataRef.current
  };
};

/**
 * Hook for ping/pong health check
 */
export const useWebSocketHealthCheck = (intervalMs: number = 30000) => {
  const { sendMessage, addEventListener, isConnected } = useWebSocket();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastPongRef = useRef<number>(Date.now());

  const sendPing = useCallback(() => {
    if (isConnected) {
      sendMessage({ type: 'ping' });
    }
  }, [isConnected, sendMessage]);

  useEffect(() => {
    const cleanup = addEventListener('pong', () => {
      lastPongRef.current = Date.now();
    });

    return cleanup;
  }, [addEventListener]);

  useEffect(() => {
    if (isConnected) {
      intervalRef.current = setInterval(sendPing, intervalMs);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isConnected, sendPing, intervalMs]);

  return {
    lastPongTime: lastPongRef.current,
    isHealthy: Date.now() - lastPongRef.current < intervalMs * 2
  };
};