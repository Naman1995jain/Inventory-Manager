'use client';

import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import Cookies from 'js-cookie';
import toast from 'react-hot-toast';

// WebSocket Message Types
export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: string;
  message?: string;
  message_type?: string;
  user?: any;
  channel?: string;
}

// Connection States
export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

interface WebSocketContextType {
  isConnected: boolean;
  connectionStatus: ConnectionStatus;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
  subscribeToChannel: (channel: string) => void;
  unsubscribeFromChannel: (channel: string) => void;
  addEventListener: (type: string, handler: (data: any) => void) => () => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
  const [isConnected, setIsConnected] = useState(false);
  
  const wsRef = useRef<WebSocket | null>(null);
  const eventListenersRef = useRef<Map<string, Set<(data: any) => void>>>(new Map());
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectInterval = useRef(1000);
  const subscribedChannelsRef = useRef<Set<string>>(new Set());

  const getWebSocketUrl = () => {
    // Prefer explicit API URL injected at build/runtime (works in Docker)
    const apiUrl = (process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || '').replace(/\/$/, '');

    if (apiUrl) {
      try {
        const url = new URL(apiUrl);
        const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
        return `${protocol}//${url.host}${url.pathname.replace(/\/$/, '')}/ws`;
      } catch (err) {
        // fallback to original behavior
        console.error('Invalid NEXT_PUBLIC_API_URL, falling back to window location', err);
      }
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.NODE_ENV === 'production'
      ? window.location.host
      : 'localhost:8000';
    return `${protocol}//${host}/api/v1/ws`;
  };

  const emitEvent = useCallback((type: string, data: any) => {
    const listeners = eventListenersRef.current.get(type);
    if (listeners) {
      listeners.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in WebSocket event handler for ${type}:`, error);
        }
      });
    }
  }, []);

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      // Handle system messages
      switch (message.type) {
        case 'authenticated':
          setIsConnected(true);
          setConnectionStatus('connected');
          reconnectAttempts.current = 0;
          reconnectInterval.current = 1000;
          toast.success('Connected to real-time updates');
          
          // Re-subscribe to channels after reconnection
          Array.from(subscribedChannelsRef.current).forEach(channel => {
            wsRef.current?.send(JSON.stringify({
              type: `subscribe_${channel}`,
            }));
          });
          break;
          
        case 'error':
          console.error('WebSocket error:', message.message);
          toast.error(message.message || 'WebSocket error');
          break;
          
        case 'subscribed':
          console.log(`Subscribed to channel: ${message.channel}`);
          break;

        case 'unsubscribed':
          console.log(`Unsubscribed from channel: ${message.channel}`);
          break;
          
        case 'low_stock_alert':
          toast.error(
            `Low stock alert: ${message.data.product_name} (${message.data.current_stock} remaining)`,
            { duration: 5000 }
          );
          break;
          
        case 'system_message':
          const toastType = message.message_type === 'error' ? 'error' : 'success';
          toast[toastType](message.message || 'System message');
          break;
      }
      
      // Emit event for components to handle
      emitEvent(message.type, message);
      
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }, [emitEvent]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const token = Cookies.get('token');
    if (!token) {
      console.warn('No authentication token found for WebSocket connection');
      return;
    }

    setConnectionStatus('connecting');
    
    try {
      const wsUrl = getWebSocketUrl();
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        
        wsRef.current?.send(JSON.stringify({
          type: 'authenticate',
          token: token
        }));
      };

      wsRef.current.onmessage = handleMessage;

      wsRef.current.onclose = (event) => {
        console.log('WebSocket connection closed:', event.code, event.reason);
        setIsConnected(false);
        setConnectionStatus('disconnected');
        
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          console.log(`Attempting to reconnect in ${reconnectInterval.current}ms`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current += 1;
            reconnectInterval.current = Math.min(reconnectInterval.current * 2, 30000);
            connect();
          }, reconnectInterval.current);
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          toast.error('Failed to maintain real-time connection. Please refresh the page.');
          setConnectionStatus('error');
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
        toast.error('Real-time connection error');
      };

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      setConnectionStatus('error');
    }
  }, [handleMessage]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setConnectionStatus('disconnected');
    subscribedChannelsRef.current.clear();
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message:', message);
    }
  }, []);

  const subscribeToChannel = useCallback((channel: string) => {
    if (subscribedChannelsRef.current.has(channel)) {
      return;
    }

    subscribedChannelsRef.current.add(channel);
    
    if (isConnected) {
      sendMessage({
        type: `subscribe_${channel}`,
      });
    }
  }, [isConnected, sendMessage]);

  const unsubscribeFromChannel = useCallback((channel: string) => {
    subscribedChannelsRef.current.delete(channel);
    
    if (isConnected) {
      sendMessage({
        type: `unsubscribe_${channel}`,
      });
    }
  }, [isConnected, sendMessage]);

  const addEventListener = useCallback((type: string, handler: (data: any) => void) => {
    if (!eventListenersRef.current.has(type)) {
      eventListenersRef.current.set(type, new Set());
    }
    eventListenersRef.current.get(type)!.add(handler);

    return () => {
      const listeners = eventListenersRef.current.get(type);
      if (listeners) {
        listeners.delete(handler);
        if (listeners.size === 0) {
          eventListenersRef.current.delete(type);
        }
      }
    };
  }, []);

  // Auto-connect when token is available
  useEffect(() => {
    const token = Cookies.get('token');
    if (token && connectionStatus === 'disconnected') {
      connect();
    }
  }, [connect, connectionStatus]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  const value: WebSocketContextType = {
    isConnected,
    connectionStatus,
    connect,
    disconnect,
    sendMessage,
    subscribeToChannel,
    unsubscribeFromChannel,
    addEventListener
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};