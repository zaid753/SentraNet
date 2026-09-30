import { useState, useEffect, useRef, useCallback } from 'react';

export type EventEnvelope = {
  event_id: string;
  event_type: string;
  timestamp: string;
  source: string;
  payload: any;
};

export type ConnectionStatus = 'connecting' | 'connected' | 'reconnecting' | 'disconnected' | 'error';

export interface UseRealtimeEventsReturn {
  status: ConnectionStatus;
  lastEvent: EventEnvelope | null;
  reconnect: () => void;
  disconnect: () => void;
  subscribe: (eventType: string, handler: (payload: any) => void) => () => void;
}

export function useRealtimeEvents(url: string): UseRealtimeEventsReturn {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [lastEvent, setLastEvent] = useState<EventEnvelope | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const backoffRef = useRef(1000);
  
  const subscribersRef = useRef<Map<string, Set<(payload: any) => void>>>(new Map());

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setStatus('connecting');
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setStatus('connected');
      backoffRef.current = 1000; // reset backoff
    };

    ws.onmessage = (event) => {
      try {
        const data: EventEnvelope = JSON.parse(event.data);
        setLastEvent(data);
        
        const handlers = subscribersRef.current.get(data.event_type);
        if (handlers) {
          handlers.forEach(handler => handler(data.payload));
        }
      } catch (err) {
        console.error('Failed to parse realtime event:', err);
      }
    };

    ws.onclose = () => {
      setStatus('disconnected');
      scheduleReconnect();
    };

    ws.onerror = () => {
      setStatus('error');
      // onclose will fire next, handling the reconnect
    };

    wsRef.current = ws;
  }, [url]);

  const scheduleReconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      window.clearTimeout(reconnectTimeoutRef.current);
    }
    
    setStatus('reconnecting');
    reconnectTimeoutRef.current = window.setTimeout(() => {
      backoffRef.current = Math.min(backoffRef.current * 1.5, 30000); // Max 30s backoff
      connect();
    }, backoffRef.current);
  }, [connect]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      window.clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      // Prevent reconnect on manual disconnect by overriding onclose
      wsRef.current.onclose = null;
      wsRef.current.close();
      wsRef.current = null;
    }
    setStatus('disconnected');
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    connect();
  }, [connect, disconnect]);

  const subscribe = useCallback((eventType: string, handler: (payload: any) => void) => {
    if (!subscribersRef.current.has(eventType)) {
      subscribersRef.current.set(eventType, new Set());
    }
    subscribersRef.current.get(eventType)!.add(handler);

    return () => {
      const handlers = subscribersRef.current.get(eventType);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          subscribersRef.current.delete(eventType);
        }
      }
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return { status, lastEvent, reconnect, disconnect, subscribe };
}
