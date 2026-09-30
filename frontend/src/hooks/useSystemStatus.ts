import { useState, useEffect, useCallback, useRef } from 'react';
import type { SystemStatus, HealthResponse, ConnectionState } from '../types';
import { getHealth, getSystemStatus } from '../services/api';

export function useSystemStatus(pollIntervalMs: number = 10000) {
  const [connectionState, setConnectionState] = useState<ConnectionState>('LOADING');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const timerRef = useRef<number | null>(null);

  const fetchStatus = useCallback(async (isManual: boolean = false) => {
    if (isManual) setIsRefreshing(true);
    try {
      const [healthData, statusData] = await Promise.all([
        getHealth(),
        getSystemStatus(),
      ]);
      setHealth(healthData);
      setSystemStatus(statusData);
      setConnectionState('CONNECTED');
      setError(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Backend connection error';
      setError(msg);
      setConnectionState('OFFLINE');
    } finally {
      if (isManual) setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();

    const handleVisibilityChange = () => {
      if (document.hidden) {
        if (timerRef.current) {
          window.clearInterval(timerRef.current);
          timerRef.current = null;
        }
      } else {
        fetchStatus();
        timerRef.current = window.setInterval(fetchStatus, pollIntervalMs);
      }
    };

    timerRef.current = window.setInterval(fetchStatus, pollIntervalMs);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [fetchStatus, pollIntervalMs]);

  return {
    connectionState,
    health,
    systemStatus,
    error,
    isRefreshing,
    refresh: () => fetchStatus(true),
  };
}
