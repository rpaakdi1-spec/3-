/**
 * useRealtimeData Hook
 * 
 * Custom React hook for WebSocket real-time data connections
 * Enhanced with exponential backoff and network status detection
 */

import { useState, useEffect, useCallback, useRef } from 'react';

interface WebSocketMessage {
  type: string;
  data?: any;
  [key: string]: any;
}

interface UseRealtimeDataOptions {
  url: string;
  token?: string;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

interface UseRealtimeDataReturn<T> {
  data: T | null;
  isConnected: boolean;
  error: string | null;
  sendMessage: (message: any) => void;
  disconnect: () => void;
  reconnect: () => void;
}

export function useRealtimeData<T = any>(
  options: UseRealtimeDataOptions
): UseRealtimeDataReturn<T> {
  const {
    url,
    token,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    autoReconnect = true,
    reconnectInterval = 1000, // Start with 1 second
    maxReconnectAttempts = 10
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnectRef = useRef(true);
  const isOnlineRef = useRef(navigator.onLine);

  // Calculate exponential backoff with jitter
  const getBackoffDelay = useCallback((attempts: number) => {
    // Exponential backoff: 1s, 2s, 4s, 8s, 16s (max 30s)
    const baseDelay = Math.min(1000 * Math.pow(2, attempts), 30000);
    // Add random jitter (±20%)
    const jitter = baseDelay * 0.2 * (Math.random() - 0.5);
    return baseDelay + jitter;
  }, []);

  const connect = useCallback(() => {
    // Check network connectivity
    if (!isOnlineRef.current) {
      console.log('⚠️ Network offline, waiting for connection...');
      setError('Network offline');
      return;
    }

    try {
      // Prevent duplicate connections
      if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
        console.log(`⚠️ WebSocket already ${wsRef.current.readyState === WebSocket.OPEN ? 'connected' : 'connecting'}`);
        return;
      }

      // Build WebSocket URL with token if provided
      const wsUrl = token ? `${url}?token=${token}` : url;
      
      console.log(`🔌 Connecting to WebSocket: ${url}`);
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log(`✅ WebSocket connected: ${url}`);
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0; // Reset counter on successful connection
        
        if (onConnect) {
          onConnect();
        }
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          // Handle ping/pong
          if (message.type === 'ping') {
            ws.send(JSON.stringify({ type: 'pong' }));
            return;
          }
          
          // Skip state update for system messages (connected, keepalive, etc.)
          // Only update state for actual data messages or messages with meaningful data
          if (message.type !== 'connected' && message.type !== 'keepalive') {
            // Update data
            setData(message.data || message);
          }
          
          // Call custom message handler (even for system messages)
          if (onMessage) {
            onMessage(message);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error(`❌ WebSocket error: ${url}`, event);
        setError('WebSocket connection error');
        
        if (onError) {
          onError(event);
        }
      };

      ws.onclose = (event) => {
        console.log(`🔌 WebSocket disconnected: ${url} (code: ${event.code}, reason: ${event.reason || 'none'})`);
        setIsConnected(false);
        wsRef.current = null;
        
        if (onDisconnect) {
          onDisconnect();
        }
        
        // Attempt reconnection with exponential backoff
        if (
          autoReconnect &&
          shouldReconnectRef.current &&
          isOnlineRef.current &&
          reconnectAttemptsRef.current < maxReconnectAttempts
        ) {
          const delay = getBackoffDelay(reconnectAttemptsRef.current);
          reconnectAttemptsRef.current += 1;
          console.log(
            `🔄 Reconnecting (${reconnectAttemptsRef.current}/${maxReconnectAttempts}) in ${(delay / 1000).toFixed(1)}s...`
          );
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError('Max reconnection attempts reached');
          console.error('❌ Max reconnection attempts reached');
        }
      };
    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setError('Failed to create WebSocket connection');
    }
  }, [
    url,
    token,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    autoReconnect,
    maxReconnectAttempts,
    getBackoffDelay
  ]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect'); // 1000 = normal closure
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    shouldReconnectRef.current = true;
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect, disconnect]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  // Network status monitoring
  useEffect(() => {
    const handleOnline = () => {
      console.log('📶 Network back online');
      isOnlineRef.current = true;
      setError(null);
      
      // Attempt to reconnect if not connected
      if (!isConnected && shouldReconnectRef.current) {
        console.log('🔄 Attempting to reconnect...');
        reconnectAttemptsRef.current = 0; // Reset attempts on network recovery
        connect();
      }
    };

    const handleOffline = () => {
      console.log('📵 Network offline');
      isOnlineRef.current = false;
      setError('Network offline');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [isConnected, connect]);

  // Connect on mount
  useEffect(() => {
    connect();
    
    // Cleanup on unmount
    return () => {
      shouldReconnectRef.current = false;
      
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmount');
      }
    };
  }, [connect]);

  return {
    data,
    isConnected,
    error,
    sendMessage,
    disconnect,
    reconnect
  };
}


/**
 * useRealtimeDashboard Hook
 * 
 * Specialized hook for dashboard real-time updates
 */

export interface DashboardMetrics {
  active_dispatches: number;
  completed_today: number;
  pending_orders: number;
  vehicles_in_transit: number;
  temperature_alerts: number;
  timestamp: string;
}

export function useRealtimeDashboard(token?: string) {
  const wsUrl = `${
    window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  }//${window.location.host}/api/v1/dispatches/ws/dashboard`;

  return useRealtimeData<DashboardMetrics>({
    url: wsUrl,
    token,
    onConnect: () => console.log('📊 Dashboard WebSocket connected'),
    onDisconnect: () => console.log('📊 Dashboard WebSocket disconnected'),
    autoReconnect: true,
    maxReconnectAttempts: 15 // Allow more attempts for dashboard
  });
}


/**
 * useRealtimeVehicle Hook
 * 
 * Specialized hook for vehicle tracking
 */

export interface VehicleLocation {
  vehicle_id: number;
  location: {
    latitude: number;
    longitude: number;
    speed: number;
    heading: number;
    temperature?: number;
  };
  timestamp: string;
}

export function useRealtimeVehicle(vehicleId: number, token?: string) {
  const wsUrl = `${
    window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  }//${window.location.host}/api/v1/ws/vehicles/${vehicleId}`;

  return useRealtimeData<VehicleLocation>({
    url: wsUrl,
    token,
    onConnect: () => console.log(`🚚 Vehicle ${vehicleId} WebSocket connected`),
    onDisconnect: () =>
      console.log(`🚚 Vehicle ${vehicleId} WebSocket disconnected`),
    autoReconnect: true
  });
}


/**
 * useRealtimeAlerts Hook
 * 
 * Specialized hook for real-time alerts
 */

export interface Alert {
  alert_type: string;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  entity_type: string;
  entity_id: number;
  data?: any;
  timestamp: string;
}

export function useRealtimeAlerts(
  token?: string,
  onAlert?: (alert: Alert) => void
) {
  const wsUrl = `${
    window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  }//${window.location.host}/api/v1/dispatches/ws/alerts`;

  return useRealtimeData<Alert>({
    url: wsUrl,
    token,
    onMessage: (message) => {
      if (message.type === 'alert' && onAlert) {
        onAlert(message as Alert);
      }
    },
    onConnect: () => console.log('🚨 Alerts WebSocket connected'),
    onDisconnect: () => console.log('🚨 Alerts WebSocket disconnected'),
    autoReconnect: true
  });
}


/**
 * useRealtimeDispatches Hook
 * 
 * Specialized hook for dispatch updates
 */

export interface DispatchUpdate {
  dispatch_id: number;
  data: any;
  timestamp: string;
}

export function useRealtimeDispatches(token?: string) {
  const wsUrl = `${
    window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  }//${window.location.host}/api/v1/ws/dispatches`;

  return useRealtimeData<DispatchUpdate>({
    url: wsUrl,
    token,
    onConnect: () => console.log('📦 Dispatches WebSocket connected'),
    onDisconnect: () => console.log('📦 Dispatches WebSocket disconnected'),
    autoReconnect: true
  });
}
