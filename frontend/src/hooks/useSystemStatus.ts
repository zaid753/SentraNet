import { useState, useEffect, useCallback, useRef } from 'react';
import type { SystemStatus, HealthResponse, ConnectionState } from '../types';
import { getHealth, getSystemStatus } from '../services/api';
import { useRealtime } from '../context/RealtimeContext';

export function useSystemStatus() {
  const [connectionState, setConnectionState] = useState<ConnectionState>('LOADING');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const timerRef = useRef<number | null>(null);

  const { status: wsStatus } = useRealtime();

  const fetchStatus = useCallback(async (isManual: boolean = false) => {
    if (isManual) setIsRefreshing(true);
    try {
      const [healthData, statusData] = await Promise.all([
        getHealth(),
        getSystemStatus(),
      ]);
      setHealth(healthData);
      setSystemStatus(statusData);
      setError(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Backend connection error';
      setError(msg);
    } finally {
      if (isManual) setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (wsStatus === 'connected') {
      setConnectionState('CONNECTED');
    } else if (wsStatus === 'connecting' || wsStatus === 'reconnecting') {
      setConnectionState('LOADING');
    } else {
      setConnectionState('OFFLINE');
    }
  }, [wsStatus]);

  useEffect(() => {
    fetchStatus();

    // Slower fallback interval for system status API
    const intervalMs = 60000; 

    const handleVisibilityChange = () => {
      if (document.hidden) {
        if (timerRef.current) {
          window.clearInterval(timerRef.current);
          timerRef.current = null;
        }
      } else {
        fetchStatus();
        timerRef.current = window.setInterval(fetchStatus, intervalMs);
      }
    };

    timerRef.current = window.setInterval(fetchStatus, intervalMs);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [fetchStatus]);

  return {
    connectionState,
    health,
    systemStatus,
    error,
    isRefreshing,
    refresh: () => fetchStatus(true),
  };
}
