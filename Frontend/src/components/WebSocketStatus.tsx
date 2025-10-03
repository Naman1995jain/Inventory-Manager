'use client';

import React from 'react';
import { useWebSocket } from '@/context/WebSocketContext';
import { useWebSocketHealthCheck } from '@/hooks/useWebSocketHooks';
import { Wifi, WifiOff, AlertTriangle, RefreshCw } from 'lucide-react';

interface WebSocketStatusProps {
  showText?: boolean;
  position?: 'fixed' | 'relative';
  className?: string;
}

const WebSocketStatus: React.FC<WebSocketStatusProps> = ({ 
  showText = false, 
  position = 'fixed',
  className = ''
}) => {
  const { isConnected, connectionStatus, connect } = useWebSocket();
  const { isHealthy } = useWebSocketHealthCheck();

  const getStatusConfig = () => {
    if (connectionStatus === 'connecting') {
      return {
        icon: RefreshCw,
        color: 'text-yellow-500',
        bgColor: 'bg-yellow-50 border-yellow-200',
        text: 'Connecting...',
        animate: 'animate-spin'
      };
    }
    
    if (isConnected && isHealthy) {
      return {
        icon: Wifi,
        color: 'text-green-500',
        bgColor: 'bg-green-50 border-green-200',
        text: 'Connected',
        animate: ''
      };
    }
    
    if (isConnected && !isHealthy) {
      return {
        icon: AlertTriangle,
        color: 'text-yellow-500',
        bgColor: 'bg-yellow-50 border-yellow-200',
        text: 'Connection unstable',
        animate: ''
      };
    }
    
    return {
      icon: WifiOff,
      color: 'text-red-500',
      bgColor: 'bg-red-50 border-red-200',
      text: 'Disconnected',
      animate: ''
    };
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  const handleReconnect = () => {
    if (!isConnected) {
      connect();
    }
  };

  const baseClasses = `
    ${position === 'fixed' ? 'fixed bottom-4 right-4 z-50' : ''}
    flex items-center gap-2 px-3 py-2 rounded-lg border text-sm font-medium
    transition-all duration-200 hover:shadow-md
    ${config.bgColor}
    ${className}
  `;

  return (
    <div 
      className={baseClasses}
      title={`Real-time connection: ${config.text}`}
      onClick={handleReconnect}
      role="button"
      tabIndex={0}
    >
      <Icon 
        size={16} 
        className={`${config.color} ${config.animate}`}
      />
      {showText && (
        <span className={config.color}>
          {config.text}
        </span>
      )}
    </div>
  );
};

export default WebSocketStatus;