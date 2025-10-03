'use client';

import { useEffect, useCallback, useRef, useState } from 'react';
import { useWebSocket } from '@/context/WebSocketContext';

/**
 * Hook for instant optimistic updates with WebSocket sync
 */
export const useOptimisticUpdates = <T>(
  initialData: T[],
  fetchFunction: () => Promise<T[]>,
  keyExtractor: (item: T) => string | number
) => {
  const [data, setData] = useState<T[]>(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const optimisticUpdatesRef = useRef<Map<string | number, T>>(new Map());

  // Add item optimistically (before server response)
  const addOptimistic = useCallback((item: T) => {
    const key = keyExtractor(item);
    optimisticUpdatesRef.current.set(key, item);
    setData(prev => [item, ...prev]);
  }, [keyExtractor]);

  // Update item optimistically
  const updateOptimistic = useCallback((item: T) => {
    const key = keyExtractor(item);
    optimisticUpdatesRef.current.set(key, item);
    setData(prev => prev.map(existing => 
      keyExtractor(existing) === key ? item : existing
    ));
  }, [keyExtractor]);

  // Remove item optimistically
  const removeOptimistic = useCallback((key: string | number) => {
    optimisticUpdatesRef.current.delete(key);
    setData(prev => prev.filter(item => keyExtractor(item) !== key));
  }, [keyExtractor]);

  // Confirm server update (remove from optimistic updates)
  const confirmUpdate = useCallback((key: string | number) => {
    optimisticUpdatesRef.current.delete(key);
  }, []);

  // Refresh from server
  const refresh = useCallback(async () => {
    setIsLoading(true);
    try {
      const serverData = await fetchFunction();
      setData(serverData);
      optimisticUpdatesRef.current.clear();
    } catch (error) {
      console.error('Error refreshing data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [fetchFunction]);

  return {
    data,
    isLoading,
    addOptimistic,
    updateOptimistic,
    removeOptimistic,
    confirmUpdate,
    refresh
  };
};

/**
 * Hook for instant product updates with optimistic UI
 */
export const useInstantProductUpdates = (onProductUpdate?: (data: any) => void) => {
  const { subscribeToChannel, unsubscribeFromChannel, addEventListener } = useWebSocket();

  useEffect(() => {
    subscribeToChannel('products');
    return () => unsubscribeFromChannel('products');
  }, [subscribeToChannel, unsubscribeFromChannel]);

  const handleProductUpdate = useCallback((message: any) => {
    // Instantly update UI
    if (onProductUpdate) {
      onProductUpdate(message);
    }
  }, [onProductUpdate]);

  useEffect(() => {
    const cleanup = addEventListener('product_updated', handleProductUpdate);
    return cleanup;
  }, [addEventListener, handleProductUpdate]);
};

/**
 * Hook for instant stock movement updates
 */
export const useInstantStockMovementUpdates = (onStockMovement?: (data: any) => void) => {
  const { subscribeToChannel, unsubscribeFromChannel, addEventListener } = useWebSocket();

  useEffect(() => {
    subscribeToChannel('stock_movements');
    return () => unsubscribeFromChannel('stock_movements');
  }, [subscribeToChannel, unsubscribeFromChannel]);

  const handleStockMovement = useCallback((message: any) => {
    if (onStockMovement) {
      onStockMovement(message);
    }
  }, [onStockMovement]);

  useEffect(() => {
    const cleanup = addEventListener('stock_movement_created', handleStockMovement);
    return cleanup;
  }, [addEventListener, handleStockMovement]);
};

/**
 * Hook for instant dashboard updates with live metrics
 */
export const useInstantDashboardUpdates = (onDashboardUpdate?: (data: any) => void) => {
  const { subscribeToChannel, unsubscribeFromChannel, addEventListener } = useWebSocket();

  useEffect(() => {
    subscribeToChannel('dashboard');
    return () => unsubscribeFromChannel('dashboard');
  }, [subscribeToChannel, unsubscribeFromChannel]);

  const handleDashboardUpdate = useCallback((message: any) => {
    if (onDashboardUpdate) {
      onDashboardUpdate(message);
    }
  }, [onDashboardUpdate]);

  useEffect(() => {
    const cleanupUpdate = addEventListener('dashboard_update', handleDashboardUpdate);
    const cleanupStats = addEventListener('dashboard_stats_update', handleDashboardUpdate);
    
    return () => {
      cleanupUpdate();
      cleanupStats();
    };
  }, [addEventListener, handleDashboardUpdate]);
};

/**
 * Hook for instant UI updates - no delays
 */
export const useInstantUI = <T>(
  fetchFunction: () => Promise<T>,
  webSocketEvents: string[] = [],
  options?: {
    refreshOnEvents?: boolean;
    optimistic?: boolean;
  }
) => {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { addEventListener } = useWebSocket();
  const { refreshOnEvents = true, optimistic = true } = options || {};

  const fetchData = useCallback(async (showLoading = true) => {
    if (showLoading) setIsLoading(true);
    try {
      const result = await fetchFunction();
      setData(result);
      return result;
    } catch (error) {
      console.error('Error fetching data:', error);
      throw error;
    } finally {
      if (showLoading) setIsLoading(false);
    }
  }, [fetchFunction]);

  // Instant update on WebSocket events
  useEffect(() => {
    if (!refreshOnEvents || webSocketEvents.length === 0) return;

    const cleanups: (() => void)[] = [];

    webSocketEvents.forEach(eventType => {
      const cleanup = addEventListener(eventType, () => {
        // Refresh data instantly without showing loading
        fetchData(false);
      });
      cleanups.push(cleanup);
    });

    return () => {
      cleanups.forEach(cleanup => cleanup());
    };
  }, [addEventListener, refreshOnEvents, webSocketEvents, fetchData]);

  // Initial load
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    isLoading,
    refresh: () => fetchData(true),
    refreshSilent: () => fetchData(false)
  };
};